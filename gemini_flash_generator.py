"""Gemini Flash - fast nutrition / recovery tips."""
from .gemini_client import GeminiUnavailable, generate_text
from .nutrition import fallback_tip


def generate_nutrition_tip_with_flash(goal: str) -> str:
    """Generate one nutrition or recovery tip for the user's fitness goal."""
    prompt = (
        f"Give one clear, helpful nutrition or recovery tip for someone focused on '{goal}'. "
        "Keep it to 2-3 sentences. The tip should be practical, friendly, and easy to understand. "
        "Return plain text only."
    )
    try:
        return generate_text(prompt, tier="flash")
    except GeminiUnavailable:
        return fallback_tip(goal)
