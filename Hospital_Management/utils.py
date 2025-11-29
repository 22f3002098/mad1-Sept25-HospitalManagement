from functools import wraps
from flask import session, flash, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to continue', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to continue', 'warning')
                return redirect(url_for('login'))
            if session.get('role') != role:
                flash('Access denied', 'danger')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def validate_phone(phone):
    if not phone:
        return False
    phone_digits = ''.join(filter(str.isdigit, phone))
    return len(phone_digits) == 10


def validate_email(email):
    return '@' in email and '.' in email
