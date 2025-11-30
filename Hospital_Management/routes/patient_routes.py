from flask import render_template, request, redirect, url_for, session, flash
from models import db, Doctor, Patient, Department, Appointment, DoctorAvailability, User
from datetime import datetime, timedelta, date
from utils import role_required, validate_phone

def patient_dashboard_view():
    departments = Department.query.all()
    today = date.today()
    week_later = today + timedelta(days=7)
    
    doctors_with_availability = db.session.query(Doctor, DoctorAvailability).join(
        DoctorAvailability
    ).filter(
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_later
    ).all()
    
    patient_id = session.get('patient_id')
    upcoming_appointments = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.appointment_date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.appointment_date).all()
    
    return render_template('patient/dashboard.html',
                         departments=departments,
                         doctors_with_availability=doctors_with_availability,
                         upcoming_appointments=upcoming_appointments)


def patient_doctors_view():
    search = request.args.get('search', '')
    department_id = request.args.get('department_id')
    
    query = Doctor.query.join(User).filter(User.is_active == True)
    
    if department_id:
        query = query.filter(Doctor.department_id == department_id)
    
    if search:
        query = query.filter(Doctor.name.like(f'%{search}%'))
    
    doctors = query.all()
    departments = Department.query.all()
    
    return render_template('patient/doctors.html',
                         doctors=doctors,
                         departments=departments,
                         search=search,
                         selected_department=department_id)


def patient_book_appointment_view(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        appointment_date_str = request.form.get('appointment_date')
        appointment_time_str = request.form.get('appointment_time')
        
        appointment_date = datetime.strptime(appointment_date_str, '%Y-%m-%d').date()
        appointment_time = datetime.strptime(appointment_time_str, '%H:%M').time()
        
        patient_id = session.get('patient_id')
        
        patient_overlap = Appointment.query.filter_by(
            patient_id=patient_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).filter(Appointment.status != 'Cancelled').first()
        
        if patient_overlap:
            flash('You already have an appointment at this time', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        
        existing = Appointment.query.filter_by(
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).filter(Appointment.status != 'Cancelled').first()
        
        if existing:
            flash('This time slot is already booked with the doctor', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        
        availability = DoctorAvailability.query.filter_by(
            doctor_id=doctor_id,
            date=appointment_date
        ).first()
        
        if not availability:
            flash('Doctor is not available on this date', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        
        if not (availability.start_time <= appointment_time <= availability.end_time):
            flash(f'Please select a time between {availability.start_time.strftime("%H:%M")} and {availability.end_time.strftime("%H:%M")}', 'danger')
            return redirect(url_for('book_appointment', doctor_id=doctor_id))
        
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )
        db.session.add(appointment)
        db.session.commit()
        
        flash('Appointment booked successfully', 'success')
        return redirect(url_for('patient_appointments'))
    
    today = date.today()
    week_later = today + timedelta(days=7)
    available_slots = DoctorAvailability.query.filter(
        DoctorAvailability.doctor_id == doctor_id,
        DoctorAvailability.date >= today,
        DoctorAvailability.date <= week_later
    ).all()
    
    return render_template('patient/book_appointment.html',
                         doctor=doctor,
                         available_slots=available_slots)


def patient_appointments_view():
    patient_id = session.get('patient_id')
    today = date.today()
    
    upcoming = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        Appointment.appointment_date >= today,
        Appointment.status == 'Booked'
    ).order_by(Appointment.appointment_date).all()
    
    past = Appointment.query.filter(
        Appointment.patient_id == patient_id,
        db.or_(
            Appointment.appointment_date < today,
            Appointment.status.in_(['Completed', 'Cancelled'])
        )
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('patient/appointments.html',
                         upcoming_appointments=upcoming,
                         past_appointments=past)


def patient_cancel_appointment_view(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if appointment.patient_id != session.get('patient_id'):
        flash('Unauthorized access', 'danger')
        return redirect(url_for('patient_appointments'))
    
    appointment.status = 'Cancelled'
    db.session.commit()
    flash('Appointment cancelled successfully', 'info')
    return redirect(url_for('patient_appointments'))


def patient_treatment_history_view():
    patient_id = session.get('patient_id')
    appointments = Appointment.query.filter_by(
        patient_id=patient_id,
        status='Completed'
    ).order_by(Appointment.appointment_date.desc()).all()
    
    return render_template('patient/history.html', appointments=appointments)


def patient_profile_view():
    patient_id = session.get('patient_id')
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'POST':
        contact = request.form.get('contact')
        
        if not validate_phone(contact):
            flash('Phone number must be exactly 10 digits', 'danger')
            return render_template('patient/profile.html', patient=patient)
        
        patient.name = request.form.get('name')
        patient.age = request.form.get('age')
        patient.gender = request.form.get('gender')
        patient.contact = contact
        patient.address = request.form.get('address')
        patient.blood_group = request.form.get('blood_group')
        
        db.session.commit()
        session['name'] = patient.name
        flash('Profile updated successfully', 'success')
        return redirect(url_for('patient_dashboard'))
    
    return render_template('patient/profile.html', patient=patient)
