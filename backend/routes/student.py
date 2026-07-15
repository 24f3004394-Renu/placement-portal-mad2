from flask import Blueprint, request, jsonify, render_template
from datetime import datetime
from utils import role_required, get_current_user
from models import db, PlacementDrive, Application, Placement, Company, Interview

bp = Blueprint('student', __name__, url_prefix='/api/student')


def drive_json(d):
    return {
        "id": d.id, "company_id": d.company_id, "company_name": d.company.name,
        "title": d.title, "description": d.description,
        "eligibility_criteria": d.eligibility_criteria, "min_cgpa": d.min_cgpa,
        "required_skills": d.required_skills, "experience": d.experience,
        "ctc": d.ctc, "location": d.location,
        "deadline": d.deadline.isoformat() if d.deadline else None,
        "status": d.status
    }


def application_json(a):
    return {
        "id": a.id, "drive_id": a.drive_id, "drive_title": a.placement_drive.title,
        "company_name": a.placement_drive.company.name, "status": a.status,
        "applied_at": a.applied_at.isoformat() if a.applied_at else None,
        "placement_id": a.placement.id if a.placement else None
    }


def interview_json(i):
    return {
        "id": i.id, "application_id": i.application_id,
        "scheduled_at": i.scheduled_at.isoformat() if i.scheduled_at else None,
        "mode": i.mode, "notes": i.notes, "feedback": i.feedback
    }


@bp.route('/dashboard', methods=['GET'])
@role_required('student')
def dashboard():
    student = get_current_user()
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.applied_at.desc()).all()

   
    notifications = Application.query.filter_by(student_id=student.id, notified=False)\
        .filter(Application.status != 'applied').all()
    notif_payload = [application_json(a) for a in notifications]
    for a in notifications:
        a.notified = True
    db.session.commit()

    return jsonify({
        "applications": [application_json(a) for a in applications],
        "notifications": notif_payload
    }), 200


@bp.route('/drives', methods=['GET'])
@role_required('student')
def drives():
    student = get_current_user()
    search = request.args.get('search', '')
    query = PlacementDrive.query.filter_by(status='approved').join(Company)\
        .filter(Company.status == 'approved').filter(Company.is_blacklisted == False)

    if search:
        query = query.filter(
            (PlacementDrive.title.ilike(f'%{search}%')) |
            (PlacementDrive.required_skills.ilike(f'%{search}%')) |
            (PlacementDrive.location.ilike(f'%{search}%')) |
            (Company.name.ilike(f'%{search}%'))
        )

    results = query.order_by(PlacementDrive.created_at.desc()).all()
    applied_ids = {a.drive_id for a in Application.query.filter_by(student_id=student.id).all()}
    return jsonify([{**drive_json(d), "already_applied": d.id in applied_ids} for d in results]), 200


@bp.route('/drives/<int:id>', methods=['GET'])
@role_required('student')
def view_drive(id):
    student = get_current_user()
    drive = PlacementDrive.query.get_or_404(id)
    already_applied = Application.query.filter_by(student_id=student.id, drive_id=id).first() is not None
    return jsonify({**drive_json(drive), "already_applied": already_applied}), 200


@bp.route('/drives/<int:id>/apply', methods=['POST'])
@role_required('student')
def apply(id):
    student = get_current_user()
    drive = PlacementDrive.query.get_or_404(id)

    if drive.company.is_blacklisted:
        return jsonify({"error": "This company has been blacklisted."}), 403
    if drive.company.status != 'approved':
        return jsonify({"error": "This company has not been approved."}), 403
    if drive.status != 'approved':
        return jsonify({"error": "This drive is not open for applications."}), 403
    if Application.query.filter_by(student_id=student.id, drive_id=id).first():
        return jsonify({"error": "You have already applied to this drive."}), 409

   
    missing = [f for f in ("cgpa", "resume") if getattr(student, f) is None]
    if missing:
        return jsonify({
            "error": "Please complete your profile (CGPA and resume) before applying.",
            "missing_fields": missing
        }), 403

    if drive.min_cgpa is not None and student.cgpa < drive.min_cgpa:
        return jsonify({"error": "Your CGPA does not meet the eligibility criteria for this drive."}), 403

    
    application = Application(student_id=student.id, drive_id=id, status='applied')
    db.session.add(application)
    db.session.commit()
    return jsonify({"message": "Application submitted successfully.", "application": application_json(application)}), 201


@bp.route('/profile', methods=['GET'])
@role_required('student')
def get_profile():
    s = get_current_user()
    return jsonify({
        "id": s.id, "name": s.name, "email": s.email, "phone": s.phone,
        "degree": s.degree, "branch": s.branch, "cgpa": s.cgpa,
        "grad_year": s.grad_year, "resume": s.resume, "skills": s.skills
    }), 200


@bp.route('/profile', methods=['PUT'])
@role_required('student')
def update_profile():
    student = get_current_user()
    data = request.form if request.form else (request.get_json(silent=True) or {})

    name = data.get('name')
    phone = data.get('phone')
    if not name or not phone:
        return jsonify({"error": "Name and Phone are required."}), 400

    cgpa = data.get('cgpa')
    grad_year = data.get('grad_year')
    try:
        if cgpa not in (None, ''):
            cgpa_val = float(cgpa)
            if cgpa_val < 0 or cgpa_val > 10:
                return jsonify({"error": "CGPA must be between 0 and 10."}), 400
            student.cgpa = cgpa_val
        if grad_year not in (None, ''):
            year_val = int(grad_year)
            if year_val < 2020 or year_val > 2035:
                return jsonify({"error": "Please enter a valid graduation year."}), 400
            student.grad_year = year_val
    except ValueError:
        return jsonify({"error": "Invalid format for CGPA or Graduation Year."}), 400

    student.name = name
    student.phone = phone
    student.degree = data.get('degree')
    student.branch = data.get('branch')
    student.skills = data.get('skills')

    resume = request.files.get('resume')
    if resume and resume.filename.lower().endswith('.pdf'):
        from werkzeug.utils import secure_filename
        from flask import current_app
        import os
        filename = secure_filename(f'resume_{student.id}.pdf')
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        resume.save(os.path.join(upload_folder, filename))
        student.resume = f"/static/uploads/{filename}"

    db.session.commit()
    return jsonify({"message": "Profile updated successfully."}), 200


@bp.route('/applications/<int:id>/interview', methods=['GET'])
@role_required('student')
def view_interviews(id):
    student = get_current_user()
    application = Application.query.get_or_404(id)
    if application.student_id != student.id:
        return jsonify({"error": "Unauthorized access."}), 403
    interviews = Interview.query.filter_by(application_id=id).order_by(Interview.scheduled_at.asc()).all()
    return jsonify([interview_json(i) for i in interviews]), 200


@bp.route('/placements/<int:id>/offer-letter', methods=['GET'])
@role_required('student')
def offer_letter(id):
    student = get_current_user()
    placement = Placement.query.get_or_404(id)
    if placement.student_id != student.id:
        return jsonify({"error": "Unauthorized access."}), 403

    if placement.offer_letter_generated_at is None:
        placement.offer_letter_generated_at = datetime.now()
        db.session.commit()

    drive = PlacementDrive.query.get(placement.drive_id)
    company = Company.query.get(placement.company_id)
    return render_template('offer_letter.html', student=student, company=company, drive=drive, placement=placement), 200


# CSV EXPORT (triggered async job)

@bp.route('/export', methods=['POST'])
@role_required('student')
def trigger_export():
    from tasks import export_applications_csv
    student = get_current_user()
    task = export_applications_csv.delay('student', student.id)
    return jsonify({"task_id": task.id, "message": "Export started."}), 202


@bp.route('/export/status/<task_id>', methods=['GET'])
@role_required('student')
def export_status(task_id):
    from tasks import export_applications_csv
    result = export_applications_csv.AsyncResult(task_id)
    payload = {"task_id": task_id, "state": result.state}
    if result.state == 'SUCCESS':
        payload["file"] = result.result["file"]
        payload["row_count"] = result.result["row_count"]
    return jsonify(payload), 200