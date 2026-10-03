"""FitBuddy - FastAPI entry point.  Run:  uvicorn app.main:app --reload"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import router

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(PROJECT_DIR, "static")
os.makedirs(os.path.join(STATIC_DIR, "images"), exist_ok=True)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()  # creates fitbuddy.db and tables on first run
    yield


app = FastAPI(title="FitBuddy - AI Fitness Plan Generator", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(router)
