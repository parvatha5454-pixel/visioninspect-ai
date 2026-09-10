# VisionInspect AI

AI-powered manufacturing defect detection and quality inspection platform.

## Project Structure

```
visioninspect-ai/
    app/          → FastAPI backend
    frontend/     → Next.js frontend
```

## Backend Setup

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # fill in your PostgreSQL credentials
```

Create the database in PostgreSQL first:
```sql
CREATE DATABASE visioninspect;
```

Run:
```bash
uvicorn app.main:app --reload
```

Visit:
- http://localhost:8000 → health check
- http://localhost:8000/docs → Swagger UI (test signup/login/upload here)

## Frontend Setup

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Visit http://localhost:3000 (redirects to `/login`).

## Loading the MVTec AD Dataset (optional, for realistic test data)

```bash
python load_mvtec_dataset.py "path\to\extracted\mvtec_ad"
python build_references.py
```

The first script loads all 15 category images into the database. The
second builds the anomaly-detection reference profile used by the defect
detection engine.

## What's Implemented

### Milestone 1 (Week 1 & 2) — Core Setup
- `app/models.py` — 6 tables: users, categories, images, inspections, defects, inspection_results
- `app/auth.py` — JWT auth (signup, login, role-based access via `require_role`)
- `app/routers/users.py` — `/users/signup`, `/users/login`, `/users/me`
- `app/routers/images.py` — `/images/upload`, `/images/`, `/images/{id}`, `/images/{id}/file`
- `app/routers/categories.py` — `/categories/` (GET open to all, POST admin-only)
- Role-based access tested end-to-end (Inspector blocked from admin actions with 403; Admin allowed with 200)
- Frontend: login, signup, dashboard (upload + browse units), inspection detail page
- MVTec AD dataset loader — loads all 15 categories, 5,000+ images

### Milestone 2 (Week 3 & 4) — Image Processing & Defect Detection
- `app/vision/preprocessing.py` — resize, grayscale, denoise, CLAHE contrast enhancement, image quality report (sharpness/brightness/blur)
- `app/vision/detector.py` — per-category reference profile (mean/std of "good" training images), anomaly scoring
- `build_references.py` — builds reference profiles for all categories
- `app/routers/inspections.py` — `/inspections/run/{image_id}` — runs detection, stores result + defect in DB
- Frontend inspection page — "Run inspection" button, live Pass/Fail badge, confidence gauge, severity-coded defect list, quality report

## Next Steps (Milestone 3 — Week 5 & 6)

- Defect classification refinement (multiple defect types per inspection)
- Full severity scoring formula (size/location/type/confidence weighted)
- Manufacturing analytics dashboard (trends, pass/fail rates, reports)
