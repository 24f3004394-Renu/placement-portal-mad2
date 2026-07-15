
import csv
import os
import smtplib
from datetime import date, datetime, timedelta
from email.message import EmailMessage

from celery.schedules import crontab

from backend.app import app, celery
from backend.models import db, Student, Company, PlacementDrive, Application, Placement, Interview

EXPORT_FOLDER = os.path.join(app.root_path, 'static', 'exports')


def send_email(to, subject, body, html=False):
    
    msg = EmailMessage()
    msg['From'] = app.config['MAIL_FROM']
    msg['To'] = to
    msg['Subject'] = subject
    if html:
        msg.set_content('This report is HTML. Open in an HTML-capable client.')
        msg.add_alternative(body, subtype='html')
    else:
        msg.set_content(body)
    try:
        with smtplib.SMTP(app.config['SMTP_HOST'], app.config['SMTP_PORT'], timeout=5) as s:
            s.send_message(msg)
        return True
    except OSError:
        print(f"[email fallback — no SMTP server running] To: {to} | {subject}\n{body[:300]}")
        return False




@celery.task(name='tasks.daily_reminder')
def daily_reminder():
    today = date.today()

    closing_soon = PlacementDrive.query.filter(
        PlacementDrive.status == 'approved',
        PlacementDrive.deadline != None,
        PlacementDrive.deadline >= today,
        PlacementDrive.deadline <= today + timedelta(days=3)
    ).all()

    deadline_reminders = 0
    if closing_soon:
        drive_lines = "\n".join(f"- {d.title} ({d.company.name}), closes {d.deadline.isoformat()}" for d in closing_soon)
        for student in Student.query.filter_by(is_blacklisted=False).all():
            applied_ids = {a.drive_id for a in student.applications}
            missing = [d for d in closing_soon if d.id not in applied_ids]
            if missing:
                send_email(student.email, "Placement drives closing soon", "These drives close within 3 days:\n" + drive_lines)
                deadline_reminders += 1

    tomorrow = today + timedelta(days=1)
    day_after = today + timedelta(days=2)
    upcoming_interviews = Interview.query.filter(
        Interview.scheduled_at >= datetime.combine(tomorrow, datetime.min.time()),
        Interview.scheduled_at < datetime.combine(day_after, datetime.min.time())
    ).all()

    interview_reminders = 0
    for iv in upcoming_interviews:
        student = iv.application.student
        drive = iv.application.placement_drive
        send_email(
            student.email, "Interview reminder — tomorrow",
            f"You have an interview tomorrow at {iv.scheduled_at.strftime('%H:%M')} "
            f"({iv.mode}) for {drive.title} at {drive.company.name}."
        )
        interview_reminders += 1

    return {"deadline_reminders": deadline_reminders, "interview_reminders": interview_reminders}


# --- Monthly report job -----------------------------------------------------

@celery.task(name='tasks.monthly_report')
def monthly_report():
    today = date.today()
    month_end = date(today.year, today.month, 1)
    month_start = (month_end - timedelta(days=1)).replace(day=1)
    start_dt = datetime.combine(month_start, datetime.min.time())
    end_dt = datetime.combine(month_end, datetime.min.time())

    drives_count = PlacementDrive.query.filter(PlacementDrive.created_at >= start_dt, PlacementDrive.created_at < end_dt).count()
    applied_count = Application.query.filter(Application.applied_at >= start_dt, Application.applied_at < end_dt).count()
    selected_count = Application.query.filter(
        Application.applied_at >= start_dt, Application.applied_at < end_dt, Application.status == 'selected'
    ).count()

    html = f"""
    <h2>Monthly Placement Activity Report — {month_start.strftime('%B %Y')}</h2>
    <table border="1" cellpadding="6">
      <tr><td>Drives conducted</td><td>{drives_count}</td></tr>
      <tr><td>Students applied</td><td>{applied_count}</td></tr>
      <tr><td>Students selected</td><td>{selected_count}</td></tr>
    </table>"""

    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@placementportal.local')
    emailed = send_email(admin_email, f"Monthly Placement Report — {month_start.strftime('%B %Y')}", html, html=True)

    return {"drives": drives_count, "applied": applied_count, "selected": selected_count, "emailed": emailed}


# --- Triggered: CSV export (student and company scoped by role+id) --------

@celery.task(name='tasks.export_applications_csv', bind=True)
def export_applications_csv(self, role, user_id):
    os.makedirs(EXPORT_FOLDER, exist_ok=True)
    filename = f"{role}_{user_id}_{self.request.id}.csv"
    path = os.path.join(EXPORT_FOLDER, filename)

    with open(path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Application Status', 'Applied Date'])

        if role == 'student':
            applications = Application.query.filter_by(student_id=user_id).all()
        else:  # company
            applications = Application.query.join(PlacementDrive).filter(PlacementDrive.company_id == user_id).all()

        for a in applications:
            writer.writerow([
                a.student_id,
                a.placement_drive.company.name,
                a.placement_drive.title,
                a.status,
                a.applied_at.isoformat() if a.applied_at else ''
            ])

    return {"file": f"static/exports/{filename}", "row_count": len(applications)}


# --- Beat schedule ----------------------------------------------------------

celery.conf.beat_schedule = {
    'daily-reminder': {
        'task': 'tasks.daily_reminder',
        'schedule': crontab(hour=8, minute=0),
    },
    'monthly-report': {
        'task': 'tasks.monthly_report',
        'schedule': crontab(day_of_month=1, hour=6, minute=0),
    },
}