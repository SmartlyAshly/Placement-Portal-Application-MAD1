# ======================================
# placement_portal/config.py
# ======================================
class Config:
    SECRET_KEY = "secret123"
    SQLALCHEMY_DATABASE_URI = "sqlite:///placement.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = "static/resumes"
