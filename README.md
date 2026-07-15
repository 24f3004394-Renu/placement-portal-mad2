# Placement Portal Application - V2

A campus recruitment platform connecting Admin, Companies, and Students. Companies post placement drives, students apply and track status through interviews and offers, and admin oversees approvals and platform activity.

## Tech Stack

**Backend:** Flask, Flask-JWT-Extended, Flask-SQLAlchemy, SQLite, Flask-CORS, Flask-Caching + Redis, Celery + Redis
**Frontend:** Vue 3 (Vite), Vue Router, Pinia, Bootstrap 5

## Project Structure

```
backend/
├── routes/        # auth.py, admin.py, company.py, student.py
├── models/        # one file per table
├── utils.py       # JWT role_required decorator, cache helpers
├── tasks.py       # Celery background jobs
├── config.py
└── app.py

frontend/
└── src/
    ├── views/      # admin/, company/, student/
    ├── stores/     # Pinia auth store
    ├── router/
    └── components/
```

## Setup

**Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
pip install -r requirements.txt
python app.py
```

**Celery worker** (separate terminal, from `backend/`):
```bash
celery -A tasks:celery worker --loglevel=info --pool=solo
```

**Redis** must be running locally on the default port before starting the backend or Celery.

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Roles

- **Admin** — pre-seeded on first run, approves/rejects companies and drives, manages blacklists, views platform stats
- **Company** — registers (pending admin approval), posts drives, manages applicants and interviews
- **Student** — registers, completes profile, applies to drives, tracks status, views offer letters

## Background Jobs

- Daily reminders for drives closing soon and upcoming interviews
- Monthly placement activity report emailed to admin
- User-triggered CSV export of application history (student and company)

## Notes

- Database is created programmatically on first run (`db.create_all()`), including a pre-seeded admin account.
- Uploaded resumes and generated exports are stored under `backend/static/`.
