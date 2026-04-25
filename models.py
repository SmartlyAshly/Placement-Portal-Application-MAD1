# ======================================
# placement_portal/models.py
# ======================================
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db = SQLAlchemy()


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)
    blacklisted = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    degree = db.Column(db.String(100))
    cgpa = db.Column(db.String(10))
    resume = db.Column(db.String(200))


class CompanyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    company_name = db.Column(db.String(100))
    website = db.Column(db.String(200))
    hr_contact = db.Column(db.String(100))


class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    eligibility = db.Column(db.String(200))
    deadline = db.Column(db.String(50))
    status = db.Column(db.String(20), default="Pending")


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'))
    status = db.Column(db.String(20), default="Applied")