
import os

class Config:
    SECRET_KEY = 'MAD2PROJECT' 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db' # tells SQLAlchemy where the database is located. 
    SQLALCHEMY_TRACK_MODIFICATIONS = False # to disable a feature that signals the application every time a change is about to be made in the database.
    UPLOAD_FOLDER = os.path.join('static', 'uploads') # where uploaded files will be stored.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # maximum file size for uploads (16 MB)
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'} # allowed file extensions for uploads

    JWT_SECRET_KEY = 'MAD2PROJECT-JWT-SECRET-KEY-2026-PLACEMENT'

    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

    SMTP_HOST = 'localhost'
    SMTP_PORT = 1025
    MAIL_FROM = 'placement-portal@localhost'
