from flask import render_template, request, redirect, url_for, session, flash
from models import db, Doctor, Patient, Appointment, Treatment, DoctorAvailability
from datetime import datetime, timedelta, date
from utils import role_required

def doctor_dashboard_view():
    doctor_id = session.get('doctor_id')
    today = date.today()
    week_later = today + timedelta(days=7)
    
    upcoming_appointments = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date >= today,
        Appointment.appointment_date <= week_later,
        Appointment.status == 'Booked'
    ).order_by(Appointment.appointment_date).all()
    
    patients = db.session.query(Patient).join(Appointment).filter(
        Appointment.doctor_id == doctor_id
    ).distinct().all()
    
    return render_template('doctor/dashboard.html',
                         upcoming_appointments=upcoming_appointments,
                         patients=patients)


def doctor_appointments_view():
    doctor_id = session.get('doctor_id')
    appointments = Appointment.query.filter_by(doctor_id=doctor_id).order_by(
        Appointment.appointment_date.desc()
    ).all()
    
    return render_template('doctor/appointments.html', appointments=appointments)


def doctor_complete_appointment_view(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    
    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis')
        prescription = request.form.get('prescription')
        notes = request.form.get('notes')
        
        treatment = Treatment(
            appointment_id=appointment_id,
            diagnosis=diagnosis,
            prescription=prescription,
            notes=notes
        )
        db.session.add(treatment)
        
        appointment.status = 'Completed'
        db.session.commit()
        
        flash('Appointment completed successfully', 'success')
        return redirect(url_for('doctor_appointments'))
    
    return render_template('doctor/complete_appointment.html', appointment=appointment)


def doctor_cancel_appointment_view(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    appointment.status = 'Cancelled'
    db.session.commit()
    flash('Appointment cancelled', 'info')
    return redirect(url_for('doctor_appointments'))


def doctor_patient_history_view(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(
        Appointment.appointment_date.desc()
    ).all()
    
    return render_template('doctor/patient_history.html', patient=patient, appointments=appointments)


def doctor_availability_view():
    doctor_id = session.get('doctor_id')
    
    if request.method == 'POST':
        DoctorAvailability.query.filter_by(doctor_id=doctor_id).delete()
        
        for i in range(7):
            available = request.form.get(f'available_{i}')
            if available:
                date_str = request.form.get(f'date_{i}')
                start_time_str = request.form.get(f'start_time_{i}')
                end_time_str = request.form.get(f'end_time_{i}')
                
                availability = DoctorAvailability(
                    doctor_id=doctor_id,
                    date=datetime.strptime(date_str, '%Y-%m-%d').date(),
                    start_time=datetime.strptime(start_time_str, '%H:%M').time(),
                    end_time=datetime.strptime(end_time_str, '%H:%M').time()
                )
                db.session.add(availability)
        
        db.session.commit()
        flash('Availability updated successfully', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    next_7_days = [(date.today() + timedelta(days=i)) for i in range(7)]
    current_availability = DoctorAvailability.query.filter_by(doctor_id=doctor_id).all()
    
    availability_dict = {}
    for avail in current_availability:
        availability_dict[avail.date] = {
            'start_time': avail.start_time.strftime('%H:%M'),
            'end_time': avail.end_time.strftime('%H:%M'),
            'is_available': True
        }
    
    return render_template('doctor/availability.html',
                         next_7_days=next_7_days,
                         availability_dict=availability_dict)
