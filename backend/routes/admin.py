from flask import Blueprint, request, jsonify
from utils import role_required, search_cache_get, search_cache_set, bump_cache_version
from models import db, Student, Company, PlacementDrive, Application

bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def company_json(c):
    return {
        "id": c.id, "name": c.name, "email": c.email, "hr_contact": c.hr_contact,
        "industry": c.industry, "status": c.status, "is_blacklisted": c.is_blacklisted
    }


def student_json(s):
    return {
        "id": s.id, "name": s.name, "email": s.email, "phone": s.phone,
        "branch": s.branch, "cgpa": s.cgpa, "is_blacklisted": s.is_blacklisted
    }


def drive_json(d):
    return {
        "id": d.id, "company_id": d.company_id, "company_name": d.company.name,
        "title": d.title, "ctc": d.ctc, "location": d.location,
        "deadline": d.deadline.isoformat() if d.deadline else None,
        "status": d.status
    }


def application_json(a):
    return {
        "id": a.id, "student_id": a.student_id, "student_name": a.student.name,
        "drive_id": a.drive_id, "drive_title": a.placement_drive.title,
        "company_name": a.placement_drive.company.name, "status": a.status,
        "applied_at": a.applied_at.isoformat() if a.applied_at else None
    }


@bp.route('/dashboard', methods=['GET'])
@role_required('admin')
def dashboard():
    return jsonify({
        'total_students': Student.query.count(),
        'total_companies': Company.query.count(),
        'total_drives': PlacementDrive.query.count(),
        'total_applications': Application.query.count(),
        'pending_companies': Company.query.filter_by(status='pending').count(),
        'pending_drives': PlacementDrive.query.filter_by(status='pending').count(),
    }), 200


# COMPANIES

@bp.route('/companies', methods=['GET'])
@role_required('admin')
def companies():
    search = request.args.get('search', '')
    cached = search_cache_get('companies', search)
    if cached is not None:
        return jsonify(cached), 200

    query = Company.query
    if search:
        query = query.filter(
            (Company.name.ilike(f'%{search}%')) | (Company.industry.ilike(f'%{search}%'))
        )
    results = query.order_by(Company.created_at.desc()).all()
    payload = [company_json(c) for c in results]
    search_cache_set('companies', search, payload)
    return jsonify(payload), 200


@bp.route('/companies/<int:id>/approve', methods=['PATCH'])
@role_required('admin')
def approve_company(id):
    company = Company.query.get_or_404(id)
    if company.is_blacklisted:
        return jsonify({"error": f"Cannot approve {company.name} because they are blacklisted."}), 409
    company.status = 'approved'
    db.session.commit()
    bump_cache_version('companies')
    return jsonify({"message": f"{company.name} approved.", "company": company_json(company)}), 200


@bp.route('/companies/<int:id>/reject', methods=['PATCH'])
@role_required('admin')
def reject_company(id):
    company = Company.query.get_or_404(id)
    company.status = 'rejected'
    db.session.commit()
    bump_cache_version('companies')
    return jsonify({"message": f"{company.name} rejected.", "company": company_json(company)}), 200


@bp.route('/companies/<int:id>/blacklist', methods=['PATCH'])
@role_required('admin')
def blacklist_company(id):
    company = Company.query.get_or_404(id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    bump_cache_version('companies')
    verb = 'blacklisted' if company.is_blacklisted else 'unblacklisted'
    return jsonify({"message": f"{company.name} {verb}.", "company": company_json(company)}), 200


# STUDENTS

@bp.route('/students', methods=['GET'])
@role_required('admin')
def students():
    search = request.args.get('search', '')
    cached = search_cache_get('students', search)
    if cached is not None:
        return jsonify(cached), 200

    query = Student.query
    if search:
        query = query.filter(
            (Student.name.ilike(f'%{search}%')) |
            (Student.email.ilike(f'%{search}%')) |
            (Student.phone.ilike(f'%{search}%')) |
            (Student.id == search if search.isdigit() else False)
        )
    results = query.order_by(Student.id.desc()).all()
    payload = [student_json(s) for s in results]
    search_cache_set('students', search, payload)
    return jsonify(payload), 200


@bp.route('/students/<int:id>', methods=['GET'])
@role_required('admin')
def view_student(id):
    student = Student.query.get_or_404(id)
    applications = Application.query.filter_by(student_id=id).all()
    return jsonify({
        "student": student_json(student),
        "applications": [application_json(a) for a in applications]
    }), 200


@bp.route('/students/<int:id>/blacklist', methods=['PATCH'])
@role_required('admin')
def blacklist_student(id):
    student = Student.query.get_or_404(id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    bump_cache_version('students')
    verb = 'blacklisted' if student.is_blacklisted else 'unblacklisted'
    return jsonify({"message": f"{student.name} {verb}.", "student": student_json(student)}), 200


# DRIVES

@bp.route('/drives', methods=['GET'])
@role_required('admin')
def drives():
    results = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()
    return jsonify([drive_json(d) for d in results]), 200


@bp.route('/drives/<int:id>/approve', methods=['PATCH'])
@role_required('admin')
def approve_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company.status != 'approved':
        return jsonify({"error": f"Cannot approve drive. {drive.company.name} must be approved first."}), 409
    drive.status = 'approved'
    db.session.commit()
    return jsonify({"message": f"{drive.title} approved.", "drive": drive_json(drive)}), 200


@bp.route('/drives/<int:id>/reject', methods=['PATCH'])
@role_required('admin')
def reject_drive(id):
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = 'rejected'
    db.session.commit()
    return jsonify({"message": f"{drive.title} rejected.", "drive": drive_json(drive)}), 200


# APPLICATIONS

@bp.route('/applications', methods=['GET'])
@role_required('admin')
def applications():
    results = Application.query.order_by(Application.applied_at.desc()).all()
    return jsonify([application_json(a) for a in results]), 200