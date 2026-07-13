from . import db

class Application(db.Model):
    __tablename__ = 'application'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    applied_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    notified = db.Column(db.Boolean, default=False, nullable=False)

    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),)

    placement = db.relationship('Placement', backref='applications', uselist=False)
