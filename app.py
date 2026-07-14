from datetime import datetime
import os

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from models import db, Admin, Company, Student, PlacementDrive, Application, Placement, Interview
from config import Config
from routes.auth import bp as auth_bp
from routes.admin import bp as admin_bp
from routes.company import bp as company_bp
from routes.student import bp as student_bp


def create_admin():
    # satisfy the requirement of a pre-existing admin user in database without registration
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')

    db.init_app(app)
    JWTManager(app)
    CORS(app)  

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    with app.app_context():
        db.create_all()
        create_admin()

    @app.route('/api/health', methods=['GET'])
    def api_health():
        return jsonify({
            "status": "Healthy",
            "database": "Connected",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "version": "2.0.0"
        }), 200

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)