"""Nutrition / recovery logic, including offline tips used if Gemini is unreachable."""

_TIPS = {
    "loss": (
        "Prioritize protein and vegetables at every meal - they keep you full longer, "
        "which makes a small calorie deficit much easier to stick to. Drink water before meals."
    ),
    "muscle": (
        "Include 20-30 g of protein in your post-workout meal and eat enough total calories. "
        "Muscle is built during recovery, so aim for 7-9 hours of sleep."
    ),
    "general": (
        "Build meals around whole foods: lean protein, colorful vegetables, whole grains and "
        "healthy fats. Drink water through the day and take real rest days."
    ),
}


def goal_category(goal: str) -> str:
    g = (goal or "").lower()
    if any(k in g for k in ("muscle", "gain", "bulk", "strength", "mass")):
        return "muscle"
    if any(k in g for k in ("loss", "lose", "fat", "slim", "weight", "cut")):
        return "loss"
    return "general"


def fallback_tip(goal: str) -> str:
    return _TIPS[goal_category(goal)]
