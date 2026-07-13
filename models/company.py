from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    hr_contact = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(150), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    is_blacklisted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    drives = db.relationship('PlacementDrive', backref='company', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_role(self):
        return 'company'
    
    def get_id(self):
        return f"company:{self.id}"