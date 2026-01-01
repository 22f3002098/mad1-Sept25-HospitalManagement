# mad1-Sept25-HospitalManagement-App

Hospitals need efficient systems to manage patients, doctors, appointments, and treatments. Currently, many hospitals use manual registers or disconnected software, which makes it difficult to manage records, avoid scheduling conflicts, and track patient history.

To build a Hospital Management System (HMS) web application that allows Admins, Doctors, and Patients to interact with the system based on their roles.

### Frameworks used

These are the mandatory frameworks on which the project has to be built.
- Flask for application back-end
- Jinja2 templating, HTML, CSS and Bootstraps for application front-end
- SQLite for database

## Key Terminologies
- Admin (Hospital Staff): A user with the highest level of access who manages doctors, appointments, and overall hospital data.
- Doctor: A medical professional registered in the system who interacts with patients via the app.
- Patient: A user who seeks medical care and interacts with doctors via the system.
- Appointment: A scheduled meeting between a patient and a doctor for consultation or treatment.

## Core Features
### Admin functionalities:
- Admin dashboard displays total number of doctors, patients, and appointments.
- Admin pre-exists in the app i.e. it is created programmatically after the creation of the database. [No admin registration allowed]
- Admin can add/update doctor profiles.
- Admin can view all upcoming and past appointments.
- Admin can search for patients or doctors and view their details.
- Admin can edit doctor details such as name, specialization etc., and also patient info if needed.
- Admin can remove/blacklist doctors and patients from the system.
### Doctor functionalities:
- Doctor’s dashboard displays upcoming appointments for the day/week.
- Doctor’s dashboard shows list of patients assigned to the doctor.
- Doctor's dashboard have the option to mark appointments as Completed or Cancelled.
- Doctors can provide their availability for the next 7 days.
- Doctors can update patient treatment history like provide diagnosis, treatment and prescriptions.
### Patient functionalities:
- Patients can register and login themselves on the app.
- Patients’ Dashboard displays all available specialization/departments
- Patients’ Dashboard displays availability of doctors for the coming 7 days (1 week) and patients can read doctors profiles.
- It displays upcoming appointments and their status.
- It shows past appointment history with diagnosis and prescriptions.
- Patients can edit their profile.
- Patients can book as well as cancel appointments with doctors.
### Other core functionalities:
- Prevent multiple appointments at the same date and time for the same doctor.
- Update appointment status dynamically (Booked → Completed → Cancelled).
- Admin and Patient is able to search for a specialization or by a doctor’s name
- Admin is able to search patients by name, ID, or contact information.
- Store all completed appointment records for each patient.
- Include diagnosis, prescriptions, and doctor notes for each visit.
- Allow patients to view their own treatment history.
- Allow doctors to view the full history of their patients for informed consultation.
