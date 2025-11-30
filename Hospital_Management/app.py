from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, User, Admin, Doctor, Patient
from utils import validate_phone, validate_email
from routes.admin_routes import *
from routes.doctor_routes import *
from routes.patient_routes import *
from utils import role_required
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hospital.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/')
def index():
    if 'user_id' in session:
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif role == 'patient':
            return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            session['user_id'] = user.id
            session['role'] = user.role
            session['email'] = user.email
            
            if user.role == 'admin':
                admin = Admin.query.filter_by(user_id=user.id).first()
                session['name'] = admin.name
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'doctor':
                doctor = Doctor.query.filter_by(user_id=user.id).first()
                session['name'] = doctor.name
                session['doctor_id'] = doctor.id
                return redirect(url_for('doctor_dashboard'))
            elif user.role == 'patient':
                patient = Patient.query.filter_by(user_id=user.id).first()
                session['name'] = patient.name
                session['patient_id'] = patient.id
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid credentials or account inactive', 'danger')
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        address = request.form.get('address')
        blood_group = request.form.get('blood_group')
        
        if not validate_email(email):
            flash('Invalid email format', 'danger')
            return redirect(url_for('register'))
        
        if not validate_phone(contact):
            flash('Phone number must be exactly 10 digits', 'danger')
            return redirect(url_for('register'))
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            return redirect(url_for('register'))
        
        user = User(email=email, role='patient')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        patient = Patient(
            user_id=user.id,
            name=name,
            age=age,
            gender=gender,
            contact=contact,
            address=address,
            blood_group=blood_group
        )
        db.session.add(patient)
        db.session.commit()
        
        flash('Registration successful! Please login', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@role_required('admin')
def admin_dashboard():
    return admin_dashboard_view()

@app.route('/admin/doctors')
@role_required('admin')
def admin_doctors():
    return admin_doctors_view()

@app.route('/admin/add_doctor', methods=['GET', 'POST'])
@role_required('admin')
def add_doctor():
    return admin_add_doctor_view()

@app.route('/admin/edit_doctor/<int:doctor_id>', methods=['GET', 'POST'])
@role_required('admin')
def edit_doctor(doctor_id):
    return admin_edit_doctor_view(doctor_id)

@app.route('/admin/delete_doctor/<int:doctor_id>')
@role_required('admin')
def delete_doctor(doctor_id):
    return admin_delete_doctor_view(doctor_id)

@app.route('/admin/patients')
@role_required('admin')
def admin_patients():
    return admin_patients_view()

@app.route('/admin/delete_patient/<int:patient_id>')
@role_required('admin')
def delete_patient(patient_id):
    return admin_delete_patient_view(patient_id)

@app.route('/admin/appointments')
@role_required('admin')
def admin_appointments():
    return admin_appointments_view()

@app.route('/admin/departments')
@role_required('admin')
def admin_departments():
    return admin_departments_view()

@app.route('/admin/add_department', methods=['GET', 'POST'])
@role_required('admin')
def add_department():
    return admin_add_department_view()

@app.route('/doctor/dashboard')
@role_required('doctor')
def doctor_dashboard():
    return doctor_dashboard_view()

@app.route('/doctor/appointments')
@role_required('doctor')
def doctor_appointments():
    return doctor_appointments_view()

@app.route('/doctor/complete_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@role_required('doctor')
def complete_appointment(appointment_id):
    return doctor_complete_appointment_view(appointment_id)

@app.route('/doctor/cancel_appointment/<int:appointment_id>')
@role_required('doctor')
def doctor_cancel_appointment(appointment_id):
    return doctor_cancel_appointment_view(appointment_id)

@app.route('/doctor/patient_history/<int:patient_id>')
@role_required('doctor')
def patient_history(patient_id):
    return doctor_patient_history_view(patient_id)

@app.route('/doctor/availability', methods=['GET', 'POST'])
@role_required('doctor')
def doctor_availability():
    return doctor_availability_view()

@app.route('/patient/dashboard')
@role_required('patient')
def patient_dashboard():
    return patient_dashboard_view()

@app.route('/patient/doctors')
@role_required('patient')
def patient_doctors():
    return patient_doctors_view()

@app.route('/patient/book_appointment/<int:doctor_id>', methods=['GET', 'POST'])
@role_required('patient')
def book_appointment(doctor_id):
    return patient_book_appointment_view(doctor_id)

@app.route('/patient/appointments')
@role_required('patient')
def patient_appointments():
    return patient_appointments_view()

@app.route('/patient/cancel_appointment/<int:appointment_id>')
@role_required('patient')
def cancel_appointment(appointment_id):
    return patient_cancel_appointment_view(appointment_id)

@app.route('/patient/history')
@role_required('patient')
def patient_treatment_history():
    return patient_treatment_history_view()

@app.route('/patient/profile', methods=['GET', 'POST'])
@role_required('patient')
def patient_profile():
    return patient_profile_view()


if __name__ == '__main__':
    app.run(debug=True)
