#Lets Start
# IITM PLACEMENT PORTAL — SUBMISSION READY (BASIC REQUIREMENTS COMPLETE)



# ======================================
# placement_portal/app.py
# ======================================
from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os

from config import Config
from models import db, User, CompanyProfile, Drive, Application

app = Flask(__name__)
app.config.from_object(Config)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        admin = User(
            name='Admin',
            email='admin@portal.com',
            password=generate_password_hash('admin123'),
            role='admin',
            approved=True
        )
        db.session.add(admin)
        db.session.commit()


@app.route('/')
def home():
    return redirect(url_for('login'))


# ---------- AUTH ----------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            role=request.form['role'],
            approved=(request.form['role'] == 'student')
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            if not user.active:
                return "Your account has been deactivated."
            login_user(user)
            if user.role == "admin":
                return redirect('/admin/dashboard')
            if  user.role == "company" and not user.approved:
                return "Your company profile is pending approval."
            elif user.role == "company":
                return redirect('/company/dashboard')
            else:
                return redirect('/student/dashboard')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ---------- ADMIN ----------
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    companies = User.query.filter_by(role='company').all()
    drives = Drive.query.all()
    return render_template('admin/dashboard.html',
                           students=User.query.filter_by(role='student').count(),
                           companies_count=len(companies),
                           drives_count=len(drives),
                           applications=Application.query.count(),
                           companies=companies,
                           drives=drives)


@app.route('/approve_company/<int:id>')
@login_required
def approve_company(id):
    user = User.query.get_or_404(id)
    user.approved = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/approve_drive/<int:id>')
@login_required
def approve_drive(id):
    drive = Drive.query.get_or_404(id)
    drive.status = 'Approved'
    db.session.commit()
    return redirect(url_for('admin_dashboard'))


@app.route('/search_students')
@login_required
def search_students():
    q = request.args.get('q', '')
    results = User.query.filter(User.role == 'student', User.name.contains(q)).all()
    return render_template('admin/companies.html', users=results)

@app.route('/blacklist/<int:id>')
@login_required
def blacklist(id):
    user = User.query.get_or_404(id)
    user.active = False
    user.blacklisted = True
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# ---------- COMPANY ----------
@app.route('/company/dashboard')
@login_required
def company_dashboard():
    drives = Drive.query.filter_by(company_id=current_user.id).all()
    return render_template('company/dashboard.html', drives=drives)


@app.route('/company/create_drive', methods=['GET', 'POST'])
@login_required
def create_drive():
    if request.method == 'POST':
        drive = Drive(
            company_id=current_user.id,
            title=request.form['title'],
            description=request.form['description'],
            eligibility=request.form['eligibility'],
            deadline=request.form['deadline']
        )
        db.session.add(drive)
        db.session.commit()
        return redirect(url_for('company_dashboard'))
    return render_template('company/create_drive.html')


@app.route('/company/edit_drive/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_drive(id):
    drive = Drive.query.get_or_404(id)
    if request.method == 'POST':
        drive.title = request.form['title']
        drive.description = request.form['description']
        drive.eligibility = request.form['eligibility']
        drive.deadline = request.form['deadline']
        db.session.commit()
        return redirect(url_for('company_dashboard'))
    return render_template('company/create_drive.html', drive=drive)


@app.route('/company/delete_drive/<int:id>')
@login_required
def delete_drive(id):
    drive = Drive.query.get_or_404(id)
    db.session.delete(drive)
    db.session.commit()
    return redirect(url_for('company_dashboard'))

@app.route('/company/close_drive/<int:id>')
@login_required
def close_drive(id):
    drive = Drive.query.get_or_404(id)
    drive.status = "Closed"
    db.session.commit()
    return redirect('/company/dashboard')


@app.route('/company/applications/<int:drive_id>')
@login_required
def company_applications(drive_id):
    apps = Application.query.filter_by(drive_id=drive_id).all()
    return render_template('company/applications.html', apps=apps)


@app.route('/update_application/<int:id>/<status>')
@login_required
def update_application(id, status):
    appn = Application.query.get_or_404(id)
    appn.status = status
    db.session.commit()
    return redirect(url_for('company_applications', drive_id=appn.drive_id))


# ---------- STUDENT ----------
@app.route('/student/dashboard')
@login_required
def student_dashboard():
    drives = Drive.query.filter_by(status='Approved').all()
    return render_template('student/dashboard.html', drives=drives)


@app.route('/student/profile', methods=['GET', 'POST'])
@login_required
def student_profile():
    if request.method == 'POST':
        current_user.phone = request.form['phone']
        current_user.degree = request.form['degree']
        current_user.cgpa = request.form['cgpa']
        file = request.files.get('resume')
        if file and file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            current_user.resume = filename
        db.session.commit()
        return redirect(url_for('student_dashboard'))
    return render_template('student/history.html', apps=[])


@app.route('/apply/<int:id>')
@login_required
def apply(id):
    existing = Application.query.filter_by(student_id=current_user.id, drive_id=id).first()
    if existing:
        return 'Already applied'
    db.session.add(Application(student_id=current_user.id, drive_id=id))
    db.session.commit()
    return redirect(url_for('student_dashboard'))


@app.route('/student/history')
@login_required
def history():
    apps = Application.query.filter_by(student_id=current_user.id).all()
    return render_template('student/history.html', apps=apps)


if __name__ == '__main__':
    app.run(debug=True)