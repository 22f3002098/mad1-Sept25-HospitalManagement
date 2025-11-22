from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Doctor, Department
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Unauthorized access')
        return redirect(url_for('auth.login'))
    doctors = Doctor.query.all()
    return render_template('admin/dashboard.html', doctors=doctors)

@admin_bp.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if current_user.role != 'admin':
        flash('Unauthorized access')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        specialization_id = request.form['specialization_id']

        user = User(username=username, password=generate_password_hash(password), role='doctor')
        db.session.add(user)
        db.session.commit()

        doctor = Doctor(user_id=user.id, name=name, specialization_id=specialization_id)
        db.session.add(doctor)
        db.session.commit()
        flash('Doctor added successfully!')
        return redirect(url_for('admin.dashboard'))

    departments = Department.query.all()
    return render_template('admin/add_doctor.html', departments=departments)

@admin_bp.route('/add_specialization', methods=['GET', 'POST'])
@login_required
def add_specialization():
    if current_user.role != 'admin':
        flash('Unauthorized access')
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if Department.query.filter_by(name=name).first():
            flash('This specialization already exists!')
            return redirect(url_for('admin.add_specialization'))
        new_dept = Department(name=name, description=description)
        db.session.add(new_dept)
        db.session.commit()
        flash('Specialization added successfully!')
        return redirect(url_for('admin.add_doctor'))
    return render_template('admin/add_specialization.html')
