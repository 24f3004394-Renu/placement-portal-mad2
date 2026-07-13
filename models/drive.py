from . import db


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drive'
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    eligibility_criteria = db.Column(db.Text, nullable=True)
    min_cgpa = db.Column(db.Float, nullable=True)
    required_skills = db.Column(db.String(300))
    experience = db.Column(db.String(100))
    ctc = db.Column(db.Integer)
    location = db.Column(db.String(150), nullable=True)
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    applications = db.relationship('Application', backref='placement_drive', lazy=True)

