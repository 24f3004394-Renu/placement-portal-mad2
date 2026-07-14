from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from celery import Celery

from models import db, Admin
from config import Config
from extensions import cache, celery
from routes.auth import bp as auth_bp
from routes.admin import bp as admin_bp
from routes.company import bp as company_bp
from routes.student import bp as student_bp

celery = Celery(__name__)


def make_celery(app):
    celery.conf.update(
        broker_url=app.config['CELERY_BROKER_URL'],
        result_backend=app.config['CELERY_RESULT_BACKEND'],
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def create_admin():
    if not Admin.query.filter_by(username='admin').first():
        admin = Admin(username='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created")


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    CORS(app) 
    make_celery(app)
    cache.init_app(app)


    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)

    with app.app_context():
        db.create_all()
        create_admin()

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)