"""Pydantic models used for validation."""
from pydantic import BaseModel, ConfigDict, Field, field_validator

VALID_INTENSITIES = ("low", "medium", "high")


class WorkoutRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    goal: str = Field(min_length=2, max_length=200)
    intensity: str = "medium"

    @field_validator("intensity")
    @classmethod
    def _check_intensity(cls, value: str) -> str:
        value = value.strip().lower()
        if value not in VALID_INTENSITIES:
            raise ValueError("must be low, medium or high")
        return value


class UserInput(WorkoutRequest):
    username: str = Field(min_length=1, max_length=60)
    user_id: int = Field(ge=1)
    age: int = Field(ge=10, le=100)
    weight: float = Field(ge=20, le=300)


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    feedback: str = Field(min_length=2, max_length=1000)
