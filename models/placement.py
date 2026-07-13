from . import db

class Placement(db.Model):
    __tablename__ = 'placement'
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    package = db.Column(db.Integer, nullable=False)
    placed_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    offer_letter_generated_at = db.Column(db.DateTime, nullable=True)

    