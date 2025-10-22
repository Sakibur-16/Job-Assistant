from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    email = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    country = db.Column(db.String(100))
    experience_years = db.Column(db.Integer)
    skills = db.Column(db.Text)  # JSON string of skills
    education = db.Column(db.Text)
    cv_filename = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    jobs = db.relationship('Job', backref='user', lazy=True)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(300))
    company = db.Column(db.String(200))
    location = db.Column(db.String(200))
    job_url = db.Column(db.String(500))
    deadline = db.Column(db.DateTime)
    source = db.Column(db.String(100))  # bdjobs, teletalk, etc.
    requirements = db.Column(db.Text)
    match_score = db.Column(db.Float)  # How well CV matches (0-100)
    is_applied = db.Column(db.Boolean, default=False)
    is_notified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    notification_date = db.Column(db.DateTime)
    message = db.Column(db.Text)
    is_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)