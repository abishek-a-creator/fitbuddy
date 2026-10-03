"""Gemini Pro - structured 7-day workout plan generator."""
from .gemini_client import GeminiUnavailable, generate_text
from .nutrition import goal_category

_SETS = {"low": 2, "medium": 3, "high": 4}

_PLANS = {
    "muscle": [
        ("Push (Chest, Shoulders, Triceps)", "Arm circles, band pull-aparts, light push-ups",
         [("Bench Press", "{s} sets of 8-12 reps"), ("Incline Dumbbell Press", "{s} sets of 8-12 reps"),
          ("Overhead Press", "{s} sets of 8-12 reps"), ("Lateral Raises", "{s} sets of 12-15 reps"),
          ("Triceps Pushdowns", "{s} sets of 10-15 reps")],
         "Static stretches for chest, shoulders and triceps (30 sec each)"),
        ("Pull (Back, Biceps)", "Cat-cow, scapular pull-ups, light rows",
         [("Pull-ups or Lat Pulldowns", "{s} sets of 8-12 reps"), ("Barbell Rows", "{s} sets of 8-12 reps"),
          ("Seated Cable Rows", "{s} sets of 10-12 reps"), ("Face Pulls", "{s} sets of 12-15 reps"),
          ("Dumbbell Curls", "{s} sets of 10-15 reps")],
         "Lat, upper back and biceps stretches (30 sec each)"),
        ("Legs & Core", "Bodyweight squats, leg swings, glute bridges",
         [("Back Squats", "{s} sets of 8-12 reps"), ("Romanian Deadlifts", "{s} sets of 8-12 reps"),
          ("Walking Lunges", "{s} sets of 10 reps per leg"), ("Hanging Knee Raises", "{s} sets of 10-15 reps"),
          ("Plank", "{s} sets of 30-60 seconds")],
         "Foam roll quads, hamstrings and glutes; hip flexor stretch"),
        ("Rest or Active Recovery", "Gentle mobility flow",
         [("Easy walk, swim or yoga", "20-30 minutes")],
         "Deep breathing and light stretching"),
        ("Upper Body (Variation)", "Arm circles, band pull-aparts, light push-ups",
         [("Incline Barbell Press", "{s} sets of 8-12 reps"), ("Chin-ups or Close-Grip Pulldowns", "{s} sets of 8-12 reps"),
          ("Arnold Press", "{s} sets of 8-12 reps"), ("T-Bar Rows", "{s} sets of 8-12 reps"),
          ("Hammer Curls", "{s} sets of 10-12 reps")],
         "Chest, back and shoulder stretches"),
        ("Lower Body & Core (Variation)", "Leg swings, goblet squats, glute bridges",
         [("Front Squats", "{s} sets of 8-12 reps"), ("Hip Thrusts", "{s} sets of 10-15 reps"),
          ("Bulgarian Split Squats", "{s} sets of 10 reps per leg"), ("Cable Crunches", "{s} sets of 15-20 reps"),
          ("Side Plank", "{s} sets of 30 seconds per side")],
         "Hamstring, quad and glute stretches"),
        ("Rest", "None needed",
         [("Light walk or full rest", "as you like")],
         "Prioritize sleep to prepare for next week"),
    ],
    "loss": [
        ("Full-Body Strength Circuit", "Jumping jacks, arm circles, bodyweight squats",
         [("Goblet Squats", "{s} sets of 12-15 reps"), ("Push-ups", "{s} sets of 10-15 reps"),
          ("Dumbbell Rows", "{s} sets of 12 reps per arm"), ("Reverse Lunges", "{s} sets of 10 reps per leg"),
          ("Plank", "{s} sets of 30-45 seconds")],
         "Full-body static stretching, 5 minutes"),
        ("HIIT Cardio", "Light jog, high knees, dynamic leg swings",
         [("Burpees", "{s} rounds of 30 seconds"), ("Mountain Climbers", "{s} rounds of 30 seconds"),
          ("Jump Squats", "{s} rounds of 30 seconds"), ("High Knees", "{s} rounds of 30 seconds"),
          ("Rest between rounds", "30-45 seconds")],
         "5 minutes easy walking, then hamstring and calf stretches"),
        ("Lower Body & Core", "Glute bridges, bodyweight squats, hip circles",
         [("Romanian Deadlifts", "{s} sets of 12 reps"), ("Step-ups", "{s} sets of 10 reps per leg"),
          ("Glute Bridges", "{s} sets of 15 reps"), ("Bicycle Crunches", "{s} sets of 20 reps"),
          ("Leg Raises", "{s} sets of 12 reps")],
         "Hip flexor, quad and hamstring stretches"),
        ("Active Recovery", "Gentle mobility flow",
         [("Brisk walk, easy cycle or yoga", "30 minutes")],
         "Foam rolling and deep breathing"),
        ("Upper Body + Cardio Finisher", "Arm circles, shoulder rolls, jumping jacks",
         [("Dumbbell Shoulder Press", "{s} sets of 12 reps"), ("Incline Push-ups", "{s} sets of 12-15 reps"),
          ("Lat Pulldowns or Pull-ups", "{s} sets of 10-12 reps"), ("Triceps Dips", "{s} sets of 10-12 reps"),
          ("Jump Rope or Rowing Finisher", "5 minutes")],
         "Chest, back and arm stretches"),
        ("Steady-State Cardio & Core", "5 minutes easy pace",
         [("Jog, cycle or elliptical", "30-40 minutes at a conversational pace"),
          ("Dead Bugs", "{s} sets of 10 reps per side"), ("Russian Twists", "{s} sets of 20 reps")],
         "Walk 5 minutes, then full-body stretching"),
        ("Rest", "None needed",
         [("Light walk or full rest", "as you like")],
         "Prioritize sleep and hydration"),
    ],
    "general": [
        ("Full Body A", "Jumping jacks, arm circles, bodyweight squats",
         [("Squats", "{s} sets of 10-12 reps"), ("Push-ups", "{s} sets of 8-12 reps"),
          ("Dumbbell Rows", "{s} sets of 10-12 reps"), ("Plank", "{s} sets of 30 seconds")],
         "Full-body stretching, 5 minutes"),
        ("Cardio", "Easy 5-minute walk",
         [("Jog, cycle or swim", "25-35 minutes at a steady pace")],
         "Calf and hamstring stretches"),
        ("Mobility & Core", "Cat-cow, hip circles, shoulder rolls",
         [("Yoga flow or mobility routine", "20 minutes"), ("Dead Bugs", "{s} sets of 10 reps per side"),
          ("Bird Dogs", "{s} sets of 10 reps per side"), ("Side Plank", "{s} sets of 20-30 seconds per side")],
         "Deep breathing, 3 minutes"),
        ("Rest or Active Recovery", "Gentle mobility flow",
         [("Easy walk", "20-30 minutes")],
         "Light stretching"),
        ("Full Body B", "Jumping jacks, leg swings, band pull-aparts",
         [("Lunges", "{s} sets of 10 reps per leg"), ("Overhead Press", "{s} sets of 10-12 reps"),
          ("Lat Pulldowns or Assisted Pull-ups", "{s} sets of 8-12 reps"), ("Glute Bridges", "{s} sets of 15 reps")],
         "Full-body stretching, 5 minutes"),
        ("Outdoor Activity", "Easy 5-minute walk",
         [("Hike, sport, cycling or a long walk", "45-60 minutes")],
         "Light stretching"),
        ("Rest", "None needed",
         [("Light walk or full rest", "as you like")],
         "Prioritize sleep and hydration"),
    ],
}


def _fallback_workout_plan(goal: str, intensity: str, reason: str) -> str:
    category = goal_category(goal)
    sets = _SETS.get((intensity or "medium").lower(), 3)
    lines = [
        f"7-Day {(intensity or 'medium').title()}-Intensity Plan: {goal}",
        f"(Built-in template plan - Gemini unavailable: {reason[:120]})",
        "",
    ]
    for number, (title, warmup, exercises, cooldown) in enumerate(_PLANS[category], start=1):
        lines.append(f"Day {number}: {title}")
        lines.append(f"Warm-up (5-10 mins): {warmup}")
        lines.append("Main Workout:")
        for name, scheme in exercises:
            lines.append(f"  - {name}: {scheme.format(s=sets)}")
        lines.append(f"Cooldown: {cooldown}")
        lines.append("")
    lines.append("Tip: increase weight or reps gradually each week, keep good form, and check "
                 "with a doctor before starting a new routine.")
    return "\n".join(lines)


def generate_workout_gemini(user_input: dict) -> str:
    """Generate a structured 7-day workout plan.

    user_input keys: goal, intensity (required); age, weight (optional).
    """
    goal = str(user_input.get("goal", "general fitness"))
    intensity = str(user_input.get("intensity", "medium"))
    about = ""
    if user_input.get("age") and user_input.get("weight"):
        about = f"The person is {user_input['age']} years old and weighs {user_input['weight']} kg.\n"

    prompt = f"""
You are a professional fitness trainer.
{about}
Create a personalized, structured 7-day workout plan for someone with the goal of "{goal}", and who prefers {intensity} intensity workouts.

Each day must include:
- A warm-up (5-10 mins)
- Main workout (targeted exercises, sets & reps)
- Cooldown or recovery tip

Format:
Day 1: <focus>
Warm-up: ...
Main Workout: ...
Cooldown: ...
(Repeat for Day 2-7, include rest or active recovery days where appropriate)

End with one short reminder to consult a doctor before starting a new routine.
"""
    try:
        return generate_text(prompt, tier="pro")
    except GeminiUnavailable as exc:
        return _fallback_workout_plan(goal, intensity, str(exc))
