# FitBuddy - AI Fitness Plan Generator (FastAPI + Gemini)

Personalized 7-day workout plans, nutrition tips, feedback-based plan updates and an admin dashboard.

## Quick start

```bash
# 1. create and activate a virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. install dependencies
pip install -r requirements.txt

# 3. add your Gemini API key (free key: https://aistudio.google.com/apikey)
cp .env.example .env              # Windows: copy .env.example .env
#    then edit .env and set GOOGLE_API_KEY=...

# 4. run (from this folder - the one containing "app/")
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000 (app) and http://127.0.0.1:8000/docs (API docs).

Python 3.9+ is recommended (3.10-3.12 tested paths). The database `fitbuddy.db` is created automatically.

## Pages and routes

| Route | Purpose |
|---|---|
| `GET /` | Input form (`index.html`) |
| `POST /generate-workout` | Form: saves user, generates plan (Gemini Pro) + tip (Gemini Flash), shows `result.html` |
| `POST /submit-feedback` | Form: revises the plan with Gemini Pro, shows the updated plan |
| `GET /view-all-users` | Admin dashboard: all users, original and updated plans (with delete) |
| `POST /generate-workout/gemini` | JSON API - plan only |
| `GET /nutrition-tip?goal=...` | JSON API - nutrition tip |
| `POST /generate-plan` | JSON API - save user + generate + store plan |
| `POST /update-plan/{user_id}` | JSON API - body `{"feedback": "..."}` |

## Structure

```
fitbuddy/
  requirements.txt  .env.example  README.md
  app/
    main.py                    FastAPI entry point
    routes.py                  all routes
    database.py                SQLAlchemy models + DB helpers
    schemas.py                 Pydantic validation
    gemini_client.py           API key, model names, fallbacks
    gemini_generator.py        Gemini Pro workout plan
    gemini_flash_generator.py  Gemini Flash nutrition tip
    updated_plan.py            feedback-based plan update
    nutrition.py               goal detection + offline tips
    templates/                 index.html, result.html, all_users.html
  static/style.css  static/images/gym-bg.jpg
```

## Important notes

* **Models:** Gemini 1.5 Pro (named in the project report) has been retired by Google, so the app uses the
  `gemini-pro-latest` / `gemini-flash-latest` aliases and tries newer/older names automatically.
  Override them in `.env` with `GEMINI_PRO_MODEL` and `GEMINI_FLASH_MODEL` if Google renames models.
* **Never crashes without AI:** if the key is missing, offline, or out of quota, FitBuddy shows a built-in
  template plan/tip (clearly labelled) instead of an error page.
* **Admin page:** `/view-all-users` has no login. Add authentication before deploying publicly.
* Run the server from the project root so `app.main:app` and `fitbuddy.db` resolve correctly.
