from models import db, User, Admin, Department
from app import app
from datetime import datetime

def init_database():
    with app.app_context():
        db.create_all()
        
        existing_admin = User.query.filter_by(email='admin@hospital.com').first()
        if not existing_admin:
            admin_user = User(
                email='admin@hospital.com',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
            
            admin_profile = Admin(
                user_id=admin_user.id,
                name='Hospital Administrator',
                contact='9999999999'
            )
            db.session.add(admin_profile)
            db.session.commit()
            
            print("Admin user created successfully")
            print("Email: admin@hospital.com")
            print("Password: admin123")
        
        departments_list = [
            {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
            {'name': 'Neurology', 'description': 'Brain and nervous system'},
            {'name': 'Orthopedics', 'description': 'Bones and joints'},
            {'name': 'Pediatrics', 'description': 'Children healthcare'},
            {'name': 'Dermatology', 'description': 'Skin disorders'},
            {'name': 'General Medicine', 'description': 'General health issues'}
        ]
        
        for dept in departments_list:
            existing = Department.query.filter_by(name=dept['name']).first()
            if not existing:
                new_dept = Department(name=dept['name'], description=dept['description'])
                db.session.add(new_dept)
        
        db.session.commit()
        print("Database initialized successfully")

if __name__ == '__main__':
    init_database()
