from flask import Blueprint, request, jsonify
from datetime import datetime, date
from utils import role_required, get_current_user
from models import db, PlacementDrive, Application, Placement, Student, Interview

bp = Blueprint('company', __name__, url_prefix='/api/company')


def drive_json(d):
    return {
        "id": d.id, "title": d.title, "description": d.description,
        "eligibility_criteria": d.eligibility_criteria, "min_cgpa": d.min_cgpa,
        "required_skills": d.required_skills, "experience": d.experience,
        "ctc": d.ctc, "location": d.location,
        "deadline": d.deadline.isoformat() if d.deadline else None,
        "status": d.status
    }


def application_json(a):
    return {
        "id": a.id, "student_id": a.student_id, "student_name": a.student.name,
        "student_email": a.student.email, "student_cgpa": a.student.cgpa,
        "drive_id": a.drive_id, "status": a.status,
        "applied_at": a.applied_at.isoformat() if a.applied_at else None
    }


def interview_json(i):
    return {
        "id": i.id, "application_id": i.application_id,
        "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
        "mode": i.mode, "notes": i.notes, "feedback": i.feedback
    }


def validate_drive_fields(data):
    min_cgpa = data.get('min_cgpa')
    ctc = data.get('ctc')
    deadline = data.get('deadline')

    try:
        if min_cgpa not in (None, ''):
            min_cgpa = float(min_cgpa)
            if min_cgpa < 0 or min_cgpa > 10:
                return None, (jsonify({"error": "CGPA must be between 0 and 10."}), 400)
        else:
            min_cgpa = None

        if ctc not in (None, ''):
            ctc = int(ctc)
            if ctc <= 0:
                return None, (jsonify({"error": "CTC must be a positive number."}), 400)
        else:
            ctc = None
    except (ValueError, TypeError):
        return None, (jsonify({"error": "Invalid numerical data entered."}), 400)

    if deadline:
        try:
            deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
        except ValueError:
            return None, (jsonify({"error": "Deadline must be in YYYY-MM-DD format."}), 400)
        if deadline < date.today():
            return None, (jsonify({"error": "Deadline cannot be in the past."}), 400)
    else:
        deadline = None

    return {"min_cgpa": min_cgpa, "ctc": ctc, "deadline": deadline}, None


@bp.route('/dashboard', methods=['GET'])
@role_required('company')
def dashboard():
    company = get_current_user()
    if company.is_blacklisted:
        return jsonify({"error": "Your company has been blacklisted.", "status": "blacklisted"}), 403
    if company.status != 'approved':
        return jsonify({"error": "Your company is pending admin approval.", "status": company.status}), 403

    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.created_at.desc()).all()
    total_applications = Application.query.join(PlacementDrive).filter(PlacementDrive.company_id == company.id).count()
    return jsonify({
        "company": {"id": company.id, "name": company.name, "status": company.status},
        "drives": [drive_json(d) for d in drives],
        "total_applications": total_applications
    }), 200

# DRIVES (create only allowed if company is approved)

@bp.route('/drives', methods=['POST'])
@role_required('company')
def create_drive():
    company = get_current_user()
    if company.is_blacklisted:
        return jsonify({"error": "Your company has been blacklisted and cannot create drives."}), 403
    if company.status != 'approved':
        return jsonify({"error": "Your company must be approved by admin before creating a drive."}), 403

    data = request.get_json(silent=True) or {}
    if not data.get('job_title'):
        return jsonify({"error": "job_title is required."}), 400

    parsed, error = validate_drive_fields(data)
    if error:
        return error

    drive = PlacementDrive(
        company_id=company.id,
        title=data.get('job_title'),
        description=data.get('description'),
        eligibility_criteria=data.get('eligibility'),
        min_cgpa=parsed['min_cgpa'],
        ctc=parsed['ctc'],
        location=data.get('location'),
        deadline=parsed['deadline'],
        required_skills=data.get('required_skills'),
        experience=data.get('experience'),
        status='pending'
    )
    db.session.add(drive)
    db.session.commit()
    return jsonify({"message": "Drive created, pending admin approval.", "drive": drive_json(drive)}), 201


@bp.route('/drives/<int:id>', methods=['PUT'])
@role_required('company')
def edit_drive(id):
    company = get_current_user()
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != company.id:
        return jsonify({"error": "Unauthorized access."}), 403
    if company.is_blacklisted:
        return jsonify({"error": "Your company has been blacklisted and cannot edit drives."}), 403

    data = request.get_json(silent=True) or {}
    parsed, error = validate_drive_fields(data)
    if error:
        return error

    drive.title = data.get('job_title', drive.title)
    drive.description = data.get('description')
    drive.eligibility_criteria = data.get('eligibility')
    drive.min_cgpa = parsed['min_cgpa']
    drive.ctc = parsed['ctc']
    drive.location = data.get('location')
    drive.deadline = parsed['deadline']
    drive.required_skills = data.get('required_skills')
    drive.experience = data.get('experience')
    drive.status = 'pending'  # any edit needs re-approval
    db.session.commit()
    return jsonify({"message": "Drive updated, pending re-approval.", "drive": drive_json(drive)}), 200


@bp.route('/drives/<int:id>/close', methods=['PATCH'])
@role_required('company')
def close_drive(id):
    company = get_current_user()
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != company.id:
        return jsonify({"error": "Unauthorized access."}), 403
    drive.status = 'closed'
    db.session.commit()
    return jsonify({"message": "Drive closed.", "drive": drive_json(drive)}), 200


@bp.route('/drives/<int:id>/applicants', methods=['GET'])
@role_required('company')
def view_applicants(id):
    company = get_current_user()
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != company.id:
        return jsonify({"error": "Unauthorized access."}), 403
    applications = Application.query.filter_by(drive_id=id).all()
    return jsonify({
        "drive": drive_json(drive),
        "applications": [application_json(a) for a in applications]
    }), 200


@bp.route('/applications/<int:id>', methods=['PATCH'])
@role_required('company')
def update_applicant(id):
    company = get_current_user()
    application = Application.query.get_or_404(id)
    if application.placement_drive.company_id != company.id:
        return jsonify({"error": "Unauthorized access."}), 403

    data = request.get_json(silent=True) or {}
    new_status = data.get('status')
    if new_status not in ('applied', 'shortlisted', 'rejected', 'selected'):
        return jsonify({"error": "status must be one of: applied, shortlisted, rejected, selected."}), 400

    application.status = new_status
    application.notified = False

    if new_status == 'selected' and not application.placement:
        drive = application.placement_drive
        placement = Placement(
            application_id=application.id,
            student_id=application.student_id,
            company_id=company.id,
            drive_id=application.drive_id,
            package=drive.ctc
        )
        db.session.add(placement)

    db.session.commit()
    return jsonify({"message": f"Status updated to {new_status}.", "application": application_json(application)}), 200


# INTERVIEWS

@bp.route('/applications/<int:id>/interview', methods=['POST'])
@role_required('company')
def schedule_interview(id):
    company = get_current_user()
    application = Application.query.get_or_404(id)
    if application.placement_drive.company_id != company.id:
        return jsonify({"error": "Unauthorized access."}), 403

    data = request.get_json(silent=True) or {}
    scheduled_at = data.get('scheduled_at')
    mode = data.get('mode')
    if not scheduled_at or not mode:
        return jsonify({"error": "scheduled_at and mode are required."}), 400

    try:
        scheduled_at = datetime.fromisoformat(scheduled_at)
    except ValueError:
        return jsonify({"error": "scheduled_at must be an ISO datetime, e.g. 2026-07-20T10:00:00."}), 400

    interview = Interview(
        application_id=application.id, scheduled_at=scheduled_at, mode=mode,
        notes=data.get('notes'), created_by_company_id=company.id
    )
    application.notified = False
    db.session.add(interview)
    db.session.commit()
    return jsonify({"message": "Interview scheduled.", "interview": interview_json(interview)}), 201


@bp.route('/applications/<int:id>/interviews', methods=['GET'])
@role_required('company')
def list_interviews(id):
    company = get_current_user()
    application = Application.query.get_or_404(id)
    if application.placement_drive.company_id != company.id:
        return jsonify({"error": "Unauthorized access."}), 403
    interviews = Interview.query.filter_by(application_id=id).order_by(Interview.scheduled_at.asc()).all()
    return jsonify([interview_json(i) for i in interviews]), 200


@bp.route('/interviews/<int:id>/feedback', methods=['PATCH'])
@role_required('company')
def interview_feedback(id):
    company = get_current_user()
    interview = Interview.query.get_or_404(id)
    if interview.created_by_company_id != company.id:
        return jsonify({"error": "Unauthorized access."}), 403

    data = request.get_json(silent=True) or {}
    feedback = data.get('feedback')
    if not feedback:
        return jsonify({"error": "feedback is required."}), 400

    interview.feedback = feedback
    interview.application.notified = False
    db.session.commit()
    return jsonify({"message": "Feedback saved.", "interview": interview_json(interview)}), 200


@bp.route('/students/<int:id>', methods=['GET'])
@role_required('company')
def view_student(id):
    student = Student.query.get_or_404(id)
    return jsonify({
        "id": student.id, "name": student.name, "email": student.email,
        "branch": student.branch, "cgpa": student.cgpa
    }), 200


# CSV EXPORT (triggered async job)

@bp.route('/export', methods=['POST'])
@role_required('company')
def trigger_export():
    from backend.tasks import export_applications_csv
    company = get_current_user()
    task = export_applications_csv.delay('company', company.id)
    return jsonify({"task_id": task.id, "message": "Export started."}), 202


@bp.route('/export/status/<task_id>', methods=['GET'])
@role_required('company')
def export_status(task_id):
    from backend.tasks import export_applications_csv
    result = export_applications_csv.AsyncResult(task_id)
    payload = {"task_id": task_id, "state": result.state}
    if result.state == 'SUCCESS':
        payload["file"] = result.result["file"]
        payload["row_count"] = result.result["row_count"]
    return jsonify(payload), 200