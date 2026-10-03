"""SQLite + SQLAlchemy storage for users and their workout plans."""
import os
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (Column, DateTime, Float, ForeignKey, Integer, String, Text,
                        create_engine)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "fitbuddy.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def _now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(60), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(200), nullable=False)
    intensity = Column(String(10), nullable=False)
    schedule = Column(Integer, default=7)
    created_at = Column(DateTime(timezone=True), default=_now)

    plan = relationship("WorkoutPlan", back_populates="user", uselist=False,
                        cascade="all, delete-orphan")


class WorkoutPlan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)

    user = relationship("User", back_populates="plan")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def _session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _user_dict(user: User) -> dict:
    created = user.created_at.strftime("%Y-%m-%d %H:%M") if user.created_at else ""
    return {"id": user.id, "name": user.name, "age": user.age, "weight": user.weight,
            "goal": user.goal, "intensity": user.intensity, "created_at": created}


def save_user(user_id: int, name: str, age: int, weight: float, goal: str, intensity: str) -> None:
    with _session() as db:
        user = db.get(User, user_id)
        if user:
            user.name, user.age, user.weight = name, age, weight
            user.goal, user.intensity = goal, intensity
        else:
            db.add(User(id=user_id, name=name, age=age, weight=weight, goal=goal,
                        intensity=intensity, schedule=7))
        db.commit()


def save_plan(user_id: int, plan: str) -> None:
    """Store a freshly generated plan (replaces any earlier plan for this user)."""
    with _session() as db:
        row = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        if row:
            row.original_plan = plan
            row.updated_plan = None
        else:
            db.add(WorkoutPlan(user_id=user_id, original_plan=plan))
        db.commit()


def update_plan(user_id: int, updated_text: str) -> bool:
    with _session() as db:
        row = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        if not row:
            return False
        row.updated_plan = updated_text
        db.commit()
        return True


def get_original_plan(user_id: int) -> Optional[str]:
    with _session() as db:
        row = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        return row.original_plan if row else None


def get_updated_plan(user_id: int) -> Optional[str]:
    with _session() as db:
        row = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        return row.updated_plan if row and row.updated_plan else None


def get_user(user_id: int) -> Optional[dict]:
    with _session() as db:
        user = db.get(User, user_id)
        return _user_dict(user) if user else None


def get_all_users() -> list:
    with _session() as db:
        return [_user_dict(u) for u in db.query(User).order_by(User.id).all()]


def get_all_plans() -> list:
    with _session() as db:
        return [{"user_id": p.user_id, "original_plan": p.original_plan,
                 "updated_plan": p.updated_plan} for p in db.query(WorkoutPlan).all()]


def get_all_user_data() -> list:
    """Users merged with their plans, for the admin dashboard."""
    plans = {p["user_id"]: p for p in get_all_plans()}
    rows = []
    for user in get_all_users():
        plan = plans.get(user["id"])
        user["original_plan"] = plan["original_plan"] if plan else "N/A"
        user["updated_plan"] = plan["updated_plan"] if plan and plan["updated_plan"] else "Not updated"
        rows.append(user)
    return rows


def delete_user(user_id: int) -> bool:
    with _session() as db:
        user = db.get(User, user_id)
        if not user:
            return False
        db.delete(user)
        db.commit()
        return True
