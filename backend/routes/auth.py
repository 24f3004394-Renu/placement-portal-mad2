from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt
from models import db, Admin, Company, Student
from utils import get_current_user

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register/student', methods=['POST'])
def register_student():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    phone = data.get('phone')

    if not all([name, email, password, phone]):
        return jsonify({"error": "name, email, password and phone are required."}), 400

    if Student.query.filter_by(email=email).first():
        return jsonify({"error": "Email already in use."}), 409

    student = Student(name=name, email=email, phone=phone)
    student.set_password(password)
    db.session.add(student)
    db.session.commit()
    return jsonify({"message": "Registration successful. Please login.", "id": student.id}), 201


@bp.route('/register/company', methods=['POST'])
def register_company():
    data = request.get_json(silent=True) or {}
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    hr_contact = data.get('hr_contact')

    if not all([name, email, password, hr_contact]):
        return jsonify({"error": "name, email, password and hr_contact are required."}), 400

    if Company.query.filter_by(email=email).first():
        return jsonify({"error": "Email already in use."}), 409

    
    company = Company(name=name, email=email, hr_contact=hr_contact)
    company.set_password(password)
    db.session.add(company)
    db.session.commit()
    return jsonify({"message": "Registration successful. Awaiting admin approval.", "id": company.id}), 201


@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "email and password are required."}), 400

    # admin logs in with username, not email 
    admin = Admin.query.filter_by(username=email).first()
    if admin and admin.check_password(password):
        token = create_access_token(identity=str(admin.id), additional_claims={'role': 'admin'})
        return jsonify({"access_token": token, "role": "admin", "id": admin.id}), 200

    company = Company.query.filter_by(email=email).first()
    if company and company.check_password(password):
        if company.is_blacklisted:
            return jsonify({"error": "This account has been blacklisted."}), 403
        token = create_access_token(identity=str(company.id), additional_claims={'role': 'company'})
        return jsonify({"access_token": token, "role": "company", "id": company.id,
                         "name": company.name, "status": company.status}), 200

    student = Student.query.filter_by(email=email).first()
    if student and student.check_password(password):
        if student.is_blacklisted:
            return jsonify({"error": "This account has been blacklisted."}), 403
        token = create_access_token(identity=str(student.id), additional_claims={'role': 'student'})
        return jsonify({"access_token": token, "role": "student", "id": student.id, "name": student.name}), 200

    return jsonify({"error": "Invalid email or password."}), 401


@bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user = get_current_user()
    if user is None:
        return jsonify({"error": "User not found."}), 404
    role = get_jwt().get('role')
    payload = {"id": user.id, "role": role}
    payload["name"] = getattr(user, 'name', getattr(user, 'username', None))
    return jsonify(payload), 200