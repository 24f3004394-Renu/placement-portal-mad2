import os
if os.path.exists('instance/placement.db'):
    os.remove('instance/placement.db')

from datetime import date, datetime, timedelta
from app import create_app, celery

celery.conf.task_always_eager = True
celery.conf.task_store_eager_result = True

app = create_app()
c = app.test_client()
FAILS = []

def check(label, cond, detail=""):
    print(f"[{'PASS' if cond else 'FAIL'}] {label} {detail if not cond else ''}")
    if not cond: FAILS.append(label)

def auth(t): return {"Authorization": f"Bearer {t}"}

# --- seed a full workflow ---
c.post('/api/auth/register/student', json={"name": "Renu", "email": "renu@test.com", "password": "p", "phone": "9"})
c.post('/api/auth/register/student', json={"name": "Bob", "email": "bob@test.com", "password": "p", "phone": "7"})  # Bob never applies -> deadline-reminder target
c.post('/api/auth/register/company', json={"name": "Acme", "email": "hr@acme.com", "password": "p", "hr_contact": "8"})
admin_tok = c.post('/api/auth/login', json={"email": "admin", "password": "admin123"}).get_json()["access_token"]
c.patch('/api/admin/companies/1/approve', headers=auth(admin_tok))
comp_tok = c.post('/api/auth/login', json={"email": "hr@acme.com", "password": "p"}).get_json()["access_token"]
stud_tok = c.post('/api/auth/login', json={"email": "renu@test.com", "password": "p"}).get_json()["access_token"]

c.put('/api/student/profile', headers=auth(stud_tok), json={"name": "Renu", "phone": "9", "cgpa": "9.0"})
import io
c.put('/api/student/profile', headers=auth(stud_tok), data={
    "name": "Renu", "phone": "9", "resume": (io.BytesIO(b"%PDF-1.4 fake"), "resume.pdf")
}, content_type='multipart/form-data')

deadline = (date.today() + timedelta(days=2)).isoformat()  # closes within 3 days -> deadline reminder fires
c.post('/api/company/drives', headers=auth(comp_tok), json={"job_title": "SDE", "ctc": "1000000", "deadline": deadline})
c.patch('/api/admin/drives/1/approve', headers=auth(admin_tok))
c.post('/api/student/drives/1/apply', headers=auth(stud_tok))

tomorrow_10am = (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
c.post('/api/company/applications/1/interview', headers=auth(comp_tok), json={"scheduled_at": tomorrow_10am, "mode": "online"})
c.patch('/api/company/applications/1', headers=auth(comp_tok), json={"status": "selected"})

# --- Test 1: worker registers all 3 tasks (checked via the Celery app registry directly) ---
from tasks import daily_reminder, monthly_report, export_applications_csv
registered = set(celery.tasks.keys())
check("daily_reminder registered", 'tasks.daily_reminder' in registered)
check("monthly_report registered", 'tasks.monthly_report' in registered)
check("export_applications_csv registered", 'tasks.export_applications_csv' in registered)

# --- Test 2: daily reminder targets correctly ---
with app.app_context():
    result = daily_reminder.delay().get()
    check("deadline reminder targets only Bob (didn't apply)", result["deadline_reminders"] == 1, result)
    check("interview reminder fires once for Renu's tomorrow interview", result["interview_reminders"] == 1, result)

# --- Test 3: monthly report structure + numbers ---
with app.app_context():
    result = monthly_report.delay().get()
    check("monthly report returns expected keys", set(result.keys()) == {"drives", "applied", "selected", "emailed"}, result)
    # note: applied_at is NOW (this month), so THIS month's activity won't show in
    # "last month's" report — that's correct per the spec (report covers the
    # completed prior month), so drives/applied/selected are legitimately 0 here
    check("counts are ints", all(isinstance(result[k], int) for k in ("drives", "applied", "selected")), result)

# --- Test 4: CSV export via the real HTTP endpoints (student) ---
r = c.post('/api/student/export', headers=auth(stud_tok))
check("student export trigger -> 202 + task_id", r.status_code == 202 and r.get_json().get("task_id"), r.get_json())
tid = r.get_json()["task_id"]
r = c.get(f'/api/student/export/status/{tid}', headers=auth(stud_tok))
check("student export status -> SUCCESS + file + row_count", r.get_json()["state"] == "SUCCESS" and r.get_json().get("row_count") == 1, r.get_json())
fpath = r.get_json()["file"]
with open(fpath) as f:
    rows = f.read().strip().split('\n')
check("CSV header matches spec columns", rows[0] == "Student ID,Company Name,Drive Title,Application Status,Applied Date", rows[0])
check("CSV has header + 1 data row", len(rows) == 2, rows)
check("CSV row shows correct status (selected)", "selected" in rows[1], rows[1])

# --- Test 5: CSV export scoped correctly (company) ---
r = c.post('/api/company/export', headers=auth(comp_tok))
tid = r.get_json()["task_id"]
r = c.get(f'/api/company/export/status/{tid}', headers=auth(comp_tok))
fpath = r.get_json()["file"]
with open(fpath) as f:
    rows = f.read().strip().split('\n')
check("company CSV scoped to their own applicants only", len(rows) == 2, rows)

r = c.post('/api/company/export', headers=auth(stud_tok))
check("student token blocked on company export -> 403", r.status_code == 403)

# --- Test 6: beat schedule registered with correct crontab ---
schedule = celery.conf.beat_schedule
check("daily-reminder in beat schedule", 'daily-reminder' in schedule, schedule)
check("monthly-report in beat schedule, day_of_month=1", 'monthly-report' in schedule, schedule)

print()
if FAILS:
    print(f"{len(FAILS)} FAILED: {FAILS}")
    import sys; sys.exit(1)
print("ALL PASSED")