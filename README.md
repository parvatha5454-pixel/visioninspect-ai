# VisionInspect AI — Backend (Week 1)

## Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your PostgreSQL credentials:

```bash
cp .env.example .env
```

Create the database in PostgreSQL first:

```sql
CREATE DATABASE visioninspect;
```

## Run

```bash
uvicorn app.main:app --reload
```

Visit:
- http://localhost:8000 → health check
- http://localhost:8000/docs → Swagger UI (test signup/login/upload here)

## What's included (Week 1 scope)

- `app/models.py` — 6 tables: users, categories, images, inspections, defects, inspection_results
- `app/auth.py` — JWT auth (signup, login, role-based access via `require_role`)
- `app/routers/users.py` — `/users/signup`, `/users/login`, `/users/me`
- `app/routers/images.py` — `/images/upload`, `/images/` (list)

## Next steps (not yet built)

- `categories` seed data / CRUD endpoints
- Inspection + defect endpoints (Week 3-4, once detection model is ready)
- MVTec AD dataset loader script
