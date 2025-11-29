from flask import render_template, request, redirect, url_for, session, flash
from models import db, User, Admin, Doctor, Patient, Appointment
from utils import role_required

def admin_dashboard_view():
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_appointments = Appointment.query.count()
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_doctors=total_doctors,
                         total_patients=total_patients,
                         total_appointments=total_appointments,
                         recent_appointments=recent_appointments)


def admin_doctors_view():
    search = request.args.get('search', '')
    from models import Department
    if search:
        doctors = Doctor.query.join(Department).filter(
            db.or_(
                Doctor.name.like(f'%{search}%'),
                Department.name.like(f'%{search}%')
            )
        ).all()
    else:
        doctors = Doctor.query.all()
    
    return render_template('admin/doctors.html', doctors=doctors, search=search)


def admin_add_doctor_view():
    from models import Department
    from utils import validate_phone, validate_email
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        department_id = request.form.get('department_id')
        qualification = request.form.get('qualification')
        contact = request.form.get('contact')
        experience = request.form.get('experience')
        
        if not validate_email(email):
            flash('Invalid email format', 'danger')
            departments = Department.query.all()
            return render_template('admin/add_doctor.html', departments=departments)
        
        if not validate_phone(contact):
            flash('Phone number must be exactly 10 digits', 'danger')
            departments = Department.query.all()
            return render_template('admin/add_doctor.html', departments=departments)
        
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered', 'danger')
            departments = Department.query.all()
            return render_template('admin/add_doctor.html', departments=departments)
        
        user = User(email=email, role='doctor')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        doctor = Doctor(
            user_id=user.id,
            name=name,
            department_id=department_id,
            qualification=qualification,
            contact=contact,
            experience_years=experience
        )
        db.session.add(doctor)
        db.session.commit()
        
        flash('Doctor added successfully', 'success')
        return redirect(url_for('admin_doctors'))
    
    departments = Department.query.all()
    return render_template('admin/add_doctor.html', departments=departments)


def admin_edit_doctor_view(doctor_id):
    from models import Department
    from utils import validate_phone
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        contact = request.form.get('contact')
        
        if not validate_phone(contact):
            flash('Phone number must be exactly 10 digits', 'danger')
            departments = Department.query.all()
            return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)
        
        doctor.name = request.form.get('name')
        doctor.department_id = request.form.get('department_id')
        doctor.qualification = request.form.get('qualification')
        doctor.contact = contact
        doctor.experience_years = request.form.get('experience')
        
        db.session.commit()
        flash('Doctor updated successfully', 'success')
        return redirect(url_for('admin_doctors'))
    
    from models import Department
    departments = Department.query.all()
    return render_template('admin/edit_doctor.html', doctor=doctor, departments=departments)


def admin_delete_doctor_view(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    user = User.query.get(doctor.user_id)
    user.is_active = False
    db.session.commit()
    flash('Doctor removed successfully', 'success')
    return redirect(url_for('admin_doctors'))


def admin_patients_view():
    search = request.args.get('search', '')
    if search:
        patients = Patient.query.filter(
            db.or_(
                Patient.name.like(f'%{search}%'),
                Patient.contact.like(f'%{search}%'),
                Patient.id == int(search) if search.isdigit() else False
            )
        ).all()
    else:
        patients = Patient.query.all()
    
    return render_template('admin/patients.html', patients=patients, search=search)


def admin_delete_patient_view(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    user = User.query.get(patient.user_id)
    user.is_active = False
    db.session.commit()
    flash('Patient removed successfully', 'success')
    return redirect(url_for('admin_patients'))


def admin_appointments_view():
    appointments = Appointment.query.order_by(Appointment.appointment_date.desc()).all()
    return render_template('admin/appointments.html', appointments=appointments)


def admin_departments_view():
    from models import Department
    departments = Department.query.all()
    return render_template('admin/departments.html', departments=departments)


def admin_add_department_view():
    from models import Department
    
    if request.method == 'POST':
        dept_name = request.form.get('name')
        dept_desc = request.form.get('description')
        
        existing = Department.query.filter_by(name=dept_name).first()
        if existing:
            flash('Department already exists', 'danger')
            return redirect(url_for('admin_departments'))
        
        new_dept = Department(name=dept_name, description=dept_desc)
        db.session.add(new_dept)
        db.session.commit()
        
        flash('Department added successfully', 'success')
        return redirect(url_for('admin_departments'))
    
    return render_template('admin/add_department.html')
