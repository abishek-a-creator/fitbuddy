"""Feedback-based plan updating (Gemini Pro)."""
from .gemini_client import GeminiUnavailable, generate_text


def update_workout_plan(original_plan: str, user_feedback: str) -> str:
    """Revise a workout plan using the user's feedback."""
    prompt = f"""
You are a professional fitness trainer assistant.

Here's the original 7-day workout plan:
{original_plan}

User Feedback:
"{user_feedback}"

Based on the feedback, revise the relevant parts of the workout plan.
Keep the format and the rest of the plan unchanged if not needed.
Return the complete updated 7-day plan as plain text (no preamble).
"""
    try:
        return generate_text(prompt, tier="pro")
    except GeminiUnavailable as exc:
        reason = str(exc)[:120]
        return (
            f"{original_plan}\n\n"
            f"--- Requested changes (Gemini unavailable: {reason}) ---\n"
            f"Your feedback: {user_feedback}\n"
            "The AI could not rewrite the plan right now. Add your API key and submit "
            "the feedback again to get a fully revised plan."
        )
