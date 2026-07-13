
import os

class Config:
    SECRET_KEY = 'MAD2PROJECT' 
    SQLALCHEMY_DATABASE_URI = 'sqlite:///placement.db' # tells SQLAlchemy where the database is located. 
    SQLALCHEMY_TRACK_MODIFICATIONS = False # to disable a feature that signals the application every time a change is about to be made in the database.
    UPLOAD_FOLDER = os.path.join('static', 'uploads') # where uploaded files will be stored.
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # maximum file size for uploads (16 MB)
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'} # allowed file extensions for uploads

   
