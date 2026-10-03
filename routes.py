"""All FitBuddy routes: HTML pages for users/admin and JSON API endpoints."""
import os
import re
from typing import Optional

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from .database import (delete_user, get_all_user_data, get_original_plan, get_updated_plan,
                       get_user, save_plan, save_user, update_plan)
from .gemini_flash_generator import generate_nutrition_tip_with_flash
from .gemini_generator import generate_workout_gemini
from .schemas import FeedbackRequest, UserInput, WorkoutRequest
from .updated_plan import update_workout_plan

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)
router = APIRouter()


def clean_plan(text: Optional[str]) -> str:
    """Strip markdown symbols so plans read nicely inside <pre> blocks."""
    if not text:
        return ""
    text = text.replace("**", "")
    text = re.sub(r"^#+\s*", "", text, flags=re.M)
    return re.sub(r"^(\s*)[*-]\s+", lambda m: m.group(1) + "\u2022 ", text, flags=re.M)


templates.env.filters["clean_plan"] = clean_plan


def _error_text(exc: ValidationError) -> str:
    parts = []
    for err in exc.errors():
        field = str(err["loc"][-1]) if err.get("loc") else "input"
        parts.append(f"{field.replace('_', ' ')}: {err['msg']}")
    return "Please fix the following - " + "; ".join(parts)


def _result_page(request: Request, user_id_text, user: Optional[dict], tip=None,
                 message=None, error=None, status_code=200):
    """Render result.html from whatever is stored for this user."""
    original = updated = None
    if user:
        original = get_original_plan(user["id"])
        updated = get_updated_plan(user["id"])
    context = {
        "username": user["name"] if user else None,
        "user_id": user["id"] if user else user_id_text,
        "age": user["age"] if user else None,
        "weight": user["weight"] if user else None,
        "goal": user["goal"] if user else None,
        "intensity": user["intensity"] if user else None,
        "workout_plan": original,
        "updated_plan": updated,
        "nutrition_tip": tip,
        "message": message,
        "error": error,
    }
    return templates.TemplateResponse(request, "result.html", context, status_code=status_code)


# ---------------------------------------------------------------- HTML pages
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"error": None, "form": {}})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(""),
    user_id: str = Form(""),
    age: str = Form(""),
    weight: str = Form(""),
    goal: str = Form(""),
    intensity: str = Form("medium"),
):
    form = {"username": username, "user_id": user_id, "age": age, "weight": weight,
            "goal": goal, "intensity": intensity}
    try:
        data = UserInput(**form)
    except ValidationError as exc:
        return templates.TemplateResponse(
            request, "index.html", {"error": _error_text(exc), "form": form}, status_code=422)

    try:
        save_user(data.user_id, data.username, data.age, data.weight, data.goal, data.intensity)
        plan = generate_workout_gemini({"goal": data.goal, "intensity": data.intensity,
                                        "age": data.age, "weight": data.weight})
        save_plan(data.user_id, plan)
        tip = generate_nutrition_tip_with_flash(data.goal)
    except Exception as exc:  # keep the page usable whatever goes wrong
        return templates.TemplateResponse(
            request, "index.html", {"error": f"Something went wrong: {exc}", "form": form},
            status_code=500)

    return _result_page(request, data.user_id, get_user(data.user_id), tip=tip)


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(request: Request, user_id: str = Form(""), feedback: str = Form("")):
    feedback = feedback.strip()
    try:
        uid = int(user_id.strip())
    except ValueError:
        return _result_page(request, user_id, None, status_code=400,
                            error="Enter the numeric User ID you used to generate your plan.")

    user = get_user(uid)
    original = get_original_plan(uid)
    if not user or not original:
        return _result_page(request, user_id, None, status_code=404,
                            error=f"No plan found for User ID {uid}. Generate a plan first.")
    if len(feedback) < 2:
        return _result_page(request, user_id, user, status_code=400,
                            error="Please write a little feedback, e.g. 'more focus on cardio'.")

    try:
        basis = get_updated_plan(uid) or original  # keep refining the latest version
        revised = update_workout_plan(basis, feedback)
        update_plan(uid, revised)
        tip = generate_nutrition_tip_with_flash(user["goal"])
    except Exception as exc:
        return _result_page(request, user_id, user, status_code=500,
                            error=f"Could not update the plan: {exc}")

    return _result_page(request, user_id, user, tip=tip,
                        message="Your plan has been updated based on your feedback!")


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    return templates.TemplateResponse(request, "all_users.html", {"users": get_all_user_data()})


@router.post("/delete-user/{user_id}")
def remove_user(user_id: int):
    delete_user(user_id)
    return RedirectResponse(url="/view-all-users", status_code=303)


# ------------------------------------------------------------- JSON API
@router.post("/generate-workout/gemini")
def generate_gemini_workout(payload: WorkoutRequest):
    """API: generate a workout with Gemini Pro (nothing is stored)."""
    result = generate_workout_gemini({"goal": payload.goal, "intensity": payload.intensity})
    return {"model": "gemini-pro", "workout_plan": result}


@router.get("/nutrition-tip")
def get_flash_tip(goal: str = Query(..., min_length=2, max_length=200)):
    """API: nutrition / recovery tip from Gemini Flash."""
    return {"goal": goal, "nutrition_tip": generate_nutrition_tip_with_flash(goal)}


@router.post("/generate-plan")
def generate_plan(user_data: UserInput):
    """API: save user info, generate a plan, store it."""
    try:
        save_user(user_data.user_id, user_data.username, user_data.age, user_data.weight,
                  user_data.goal, user_data.intensity)
        plan = generate_workout_gemini({"goal": user_data.goal, "intensity": user_data.intensity,
                                        "age": user_data.age, "weight": user_data.weight})
        save_plan(user_data.user_id, plan)
        return {"message": "Workout plan generated and saved successfully!", "workout_plan": plan}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {exc}")


@router.post("/update-plan/{user_id}")
def update_user_plan(user_id: int, data: FeedbackRequest):
    """API: revise a stored plan using feedback."""
    original = get_updated_plan(user_id) or get_original_plan(user_id)
    if not original:
        raise HTTPException(status_code=404, detail="Original plan not found for this user.")
    revised = update_workout_plan(original, data.feedback)
    update_plan(user_id, revised)
    return {"updated_plan": revised}
