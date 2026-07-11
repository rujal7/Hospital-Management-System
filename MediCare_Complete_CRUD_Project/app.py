import os
from datetime import date, datetime, time, timedelta
from urllib.parse import quote_plus
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'development-key')
user = os.getenv('MYSQL_USER')
password = os.getenv('MYSQL_PASSWORD')
host = os.getenv('MYSQL_HOST', 'localhost')
port = os.getenv('MYSQL_PORT', '3306')
database = os.getenv('MYSQL_DATABASE', 'medicare_hms')
if user and password:
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{user}:{quote_plus(password)}@{host}:{port}/{database}'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medicare.db'
    print('WARNING: No MySQL configuration found. Using local SQLite database at medicare.db.')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def parse_date(value):
    return datetime.strptime(value, '%Y-%m-%d').date() if value else None

def parse_time(value):
    return datetime.strptime(value, '%H:%M').time() if value else None

def number(value, default=0):
    try: return Decimal(value or default)
    except Exception: return Decimal(default)

class User(db.Model):
    __tablename__='users'; id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(100),nullable=False); email=db.Column(db.String(120),unique=True,nullable=False); password_hash=db.Column(db.String(255),nullable=False); role=db.Column(db.String(30),default='patient'); active=db.Column(db.Boolean,default=True)
class Patient(db.Model):
    __tablename__='patients'; id=db.Column(db.Integer,primary_key=True); patient_code=db.Column(db.String(20),unique=True); name=db.Column(db.String(100),nullable=False); dob=db.Column(db.Date); gender=db.Column(db.String(20)); blood_group=db.Column(db.String(5)); phone=db.Column(db.String(20)); emergency_contact=db.Column(db.String(120)); address=db.Column(db.Text); allergies=db.Column(db.Text); previous_diseases=db.Column(db.Text); insurance=db.Column(db.String(150))
class Doctor(db.Model):
    __tablename__='doctors'; id=db.Column(db.Integer,primary_key=True); doctor_code=db.Column(db.String(20),unique=True); name=db.Column(db.String(100),nullable=False); department=db.Column(db.String(80)); qualification=db.Column(db.String(120)); experience=db.Column(db.Integer,default=0); fee=db.Column(db.Numeric(10,2),default=0); phone=db.Column(db.String(20)); available=db.Column(db.Boolean,default=True)
class Appointment(db.Model):
    __tablename__='appointments'; id=db.Column(db.Integer,primary_key=True); patient_id=db.Column(db.Integer,db.ForeignKey('patients.id')); doctor_id=db.Column(db.Integer,db.ForeignKey('doctors.id')); appointment_date=db.Column(db.Date); appointment_time=db.Column(db.Time); appointment_type=db.Column(db.String(30)); reason=db.Column(db.Text); status=db.Column(db.String(30),default='Scheduled'); queue_number=db.Column(db.Integer); patient=db.relationship('Patient'); doctor=db.relationship('Doctor')
class Medicine(db.Model):
    __tablename__='medicines'; id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120),nullable=False); batch_no=db.Column(db.String(50)); stock=db.Column(db.Integer,default=0); price=db.Column(db.Numeric(10,2),default=0); expiry_date=db.Column(db.Date); supplier=db.Column(db.String(120))
class LabTest(db.Model):
    __tablename__='lab_tests'; id=db.Column(db.Integer,primary_key=True); patient_id=db.Column(db.Integer,db.ForeignKey('patients.id')); test_name=db.Column(db.String(100)); test_date=db.Column(db.Date); status=db.Column(db.String(30),default='Pending'); result=db.Column(db.Text); patient=db.relationship('Patient')
class Bed(db.Model):
    __tablename__='beds'; id=db.Column(db.Integer,primary_key=True); bed_number=db.Column(db.String(20),unique=True); ward_type=db.Column(db.String(50)); status=db.Column(db.String(20),default='Available'); patient_id=db.Column(db.Integer,db.ForeignKey('patients.id'),nullable=True)
class Bill(db.Model):
    __tablename__='bills'; id=db.Column(db.Integer,primary_key=True); patient_id=db.Column(db.Integer,db.ForeignKey('patients.id')); consultation=db.Column(db.Numeric(10,2),default=0); medicine=db.Column(db.Numeric(10,2),default=0); lab=db.Column(db.Numeric(10,2),default=0); room=db.Column(db.Numeric(10,2),default=0); surgery=db.Column(db.Numeric(10,2),default=0); discount=db.Column(db.Numeric(10,2),default=0); insurance_deduction=db.Column(db.Numeric(10,2),default=0); payment_method=db.Column(db.String(30)); status=db.Column(db.String(20),default='Pending'); patient=db.relationship('Patient')
class Ambulance(db.Model):
    __tablename__='ambulances'; id=db.Column(db.Integer,primary_key=True); vehicle_number=db.Column(db.String(30),unique=True); driver_name=db.Column(db.String(100)); driver_phone=db.Column(db.String(20)); ambulance_type=db.Column(db.String(80)); status=db.Column(db.String(30),default='Available')

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user_id'): return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper

@app.route('/', methods=['GET','POST'])
def login():
    if request.method=='POST':
        u=User.query.filter_by(email=request.form['email']).first()
        if u and check_password_hash(u.password_hash,request.form['password']):
            session.update(user_id=u.id,name=u.name,role=u.role); return redirect(url_for('dashboard'))
        flash('Invalid email or password','error')
    return render_template('login.html')

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', patients=Patient.query.count(), doctors=Doctor.query.count(), appointments=Appointment.query.filter_by(appointment_date=date.today()).count(), beds=Bed.query.filter_by(status='Available').count(), recent=Appointment.query.order_by(Appointment.id.desc()).limit(6).all())

@app.route('/patients', methods=['GET','POST'])
@login_required
def patients():
    if request.method=='POST':
        try:
            p=Patient(name=request.form['name'].strip(),dob=parse_date(request.form.get('dob')),gender=request.form.get('gender'),blood_group=request.form.get('blood_group'),phone=request.form.get('phone'),emergency_contact=request.form.get('emergency_contact'),address=request.form.get('address'),allergies=request.form.get('allergies'),previous_diseases=request.form.get('previous_diseases'),insurance=request.form.get('insurance')); db.session.add(p); db.session.flush(); p.patient_code=f'PT-{p.id:04d}'; db.session.commit(); flash('Patient registered successfully','success')
        except Exception as e: db.session.rollback(); flash(f'Unable to add patient: {e}','error')
        return redirect(url_for('patients'))
    q=request.args.get('q',''); records=Patient.query.filter(Patient.name.like(f'%{q}%')).all() if q else Patient.query.order_by(Patient.id.desc()).all(); return render_template('patients.html',records=records)

@app.route('/doctors', methods=['GET','POST'])
@login_required
def doctors():
    if request.method=='POST':
        try:
            d=Doctor(name=request.form['name'].strip(),department=request.form.get('department'),qualification=request.form.get('qualification'),experience=int(request.form.get('experience') or 0),fee=number(request.form.get('fee')),phone=request.form.get('phone')); db.session.add(d); db.session.flush(); d.doctor_code=f'DR-{d.id:03d}'; db.session.commit(); flash('Doctor added successfully','success')
        except Exception as e: db.session.rollback(); flash(f'Unable to add doctor: {e}','error')
        return redirect(url_for('doctors'))
    return render_template('doctors.html',records=Doctor.query.all())

@app.route('/appointments', methods=['GET','POST'])
@login_required
def appointments():
    if request.method=='POST':
        try:
            selected_date=parse_date(request.form.get('appointment_date')); a=Appointment(patient_id=int(request.form['patient_id']),doctor_id=int(request.form['doctor_id']),appointment_date=selected_date,appointment_time=parse_time(request.form.get('appointment_time')),appointment_type=request.form.get('appointment_type'),reason=request.form.get('reason'),status='Scheduled',queue_number=Appointment.query.filter_by(appointment_date=selected_date).count()+1); db.session.add(a); db.session.commit(); flash('Appointment booked successfully','success')
        except Exception as e: db.session.rollback(); flash(f'Unable to book appointment: {e}','error')
        return redirect(url_for('appointments'))
    return render_template('appointments.html',records=Appointment.query.order_by(Appointment.appointment_date.desc()).all(),patients=Patient.query.all(),doctors=Doctor.query.filter_by(available=True).all())

@app.route('/module/<name>', methods=['GET','POST'])
@login_required
def module(name):
    models={'pharmacy':Medicine,'laboratory':LabTest,'beds':Bed,'billing':Bill,'ambulances':Ambulance}
    if name not in models: flash('Invalid module','error'); return redirect(url_for('dashboard'))
    if request.method=='POST':
        try:
            if name=='pharmacy': record=Medicine(name=request.form['name'].strip(),batch_no=request.form.get('batch_no'),stock=int(request.form.get('stock') or 0),price=number(request.form.get('price')),expiry_date=parse_date(request.form.get('expiry_date')),supplier=request.form.get('supplier'))
            elif name=='laboratory': record=LabTest(patient_id=int(request.form['patient_id']),test_name=request.form['test_name'],test_date=parse_date(request.form.get('test_date')) or date.today(),status=request.form.get('status','Pending'),result=request.form.get('result'))
            elif name=='beds': record=Bed(bed_number=request.form['bed_number'].strip(),ward_type=request.form.get('ward_type'),status=request.form.get('status','Available'),patient_id=int(request.form['patient_id']) if request.form.get('patient_id') else None)
            elif name=='billing': record=Bill(patient_id=int(request.form['patient_id']),consultation=number(request.form.get('consultation')),medicine=number(request.form.get('medicine')),lab=number(request.form.get('lab')),room=number(request.form.get('room')),surgery=number(request.form.get('surgery')),discount=number(request.form.get('discount')),insurance_deduction=number(request.form.get('insurance_deduction')),payment_method=request.form.get('payment_method'),status=request.form.get('status','Pending'))
            else: record=Ambulance(vehicle_number=request.form['vehicle_number'].strip(),driver_name=request.form.get('driver_name'),driver_phone=request.form.get('driver_phone'),ambulance_type=request.form.get('ambulance_type'),status=request.form.get('status','Available'))
            db.session.add(record); db.session.commit(); flash(f'{name.title()} record added successfully','success')
        except Exception as e: db.session.rollback(); flash(f'Unable to add record: {e}','error')
        return redirect(url_for('module',name=name))
    model=models[name]; return render_template('module.html',name=name.title(),module_name=name,records=model.query.order_by(model.id.desc()).all(),patients=Patient.query.order_by(Patient.name).all())

ENTITY_MODELS={'patient':Patient,'doctor':Doctor,'appointment':Appointment,'medicine':Medicine,'lab':LabTest,'bed':Bed,'bill':Bill,'ambulance':Ambulance}

@app.route('/edit/<entity>/<int:record_id>',methods=['GET','POST'])
@login_required
def edit_record(entity,record_id):
    model=ENTITY_MODELS.get(entity)
    if not model: flash('Invalid record type','error'); return redirect(url_for('dashboard'))
    record=db.session.get(model,record_id)
    if not record: flash('Record not found','error'); return redirect(url_for('dashboard'))
    if request.method=='POST':
        try:
            if entity=='patient':
                record.name=request.form['name']; record.dob=parse_date(request.form.get('dob')); record.gender=request.form.get('gender'); record.blood_group=request.form.get('blood_group'); record.phone=request.form.get('phone'); record.emergency_contact=request.form.get('emergency_contact'); record.address=request.form.get('address'); record.allergies=request.form.get('allergies'); record.previous_diseases=request.form.get('previous_diseases'); record.insurance=request.form.get('insurance')
            elif entity=='doctor':
                record.name=request.form['name']; record.department=request.form.get('department'); record.qualification=request.form.get('qualification'); record.experience=int(request.form.get('experience') or 0); record.fee=number(request.form.get('fee')); record.phone=request.form.get('phone'); record.available=request.form.get('available')=='1'
            elif entity=='appointment':
                record.patient_id=int(request.form['patient_id']); record.doctor_id=int(request.form['doctor_id']); record.appointment_date=parse_date(request.form.get('appointment_date')); record.appointment_time=parse_time(request.form.get('appointment_time')); record.appointment_type=request.form.get('appointment_type'); record.reason=request.form.get('reason'); record.status=request.form.get('status'); record.queue_number=int(request.form.get('queue_number') or 1)
            elif entity=='medicine':
                record.name=request.form['name']; record.batch_no=request.form.get('batch_no'); record.stock=int(request.form.get('stock') or 0); record.price=number(request.form.get('price')); record.expiry_date=parse_date(request.form.get('expiry_date')); record.supplier=request.form.get('supplier')
            elif entity=='lab':
                record.patient_id=int(request.form['patient_id']); record.test_name=request.form['test_name']; record.test_date=parse_date(request.form.get('test_date')); record.status=request.form.get('status'); record.result=request.form.get('result')
            elif entity=='bed':
                record.bed_number=request.form['bed_number']; record.ward_type=request.form.get('ward_type'); record.status=request.form.get('status'); record.patient_id=int(request.form['patient_id']) if request.form.get('patient_id') else None
            elif entity=='bill':
                record.patient_id=int(request.form['patient_id']); record.consultation=number(request.form.get('consultation')); record.medicine=number(request.form.get('medicine')); record.lab=number(request.form.get('lab')); record.room=number(request.form.get('room')); record.surgery=number(request.form.get('surgery')); record.discount=number(request.form.get('discount')); record.insurance_deduction=number(request.form.get('insurance_deduction')); record.payment_method=request.form.get('payment_method'); record.status=request.form.get('status')
            else:
                record.vehicle_number=request.form['vehicle_number']; record.driver_name=request.form.get('driver_name'); record.driver_phone=request.form.get('driver_phone'); record.ambulance_type=request.form.get('ambulance_type'); record.status=request.form.get('status')
            db.session.commit(); flash('Record updated successfully','success'); return redirect(entity_return_url(entity))
        except Exception as e: db.session.rollback(); flash(f'Unable to update record: {e}','error')
    return render_template('edit.html',entity=entity,record=record,patients=Patient.query.order_by(Patient.name).all(),doctors=Doctor.query.order_by(Doctor.name).all())

def entity_return_url(entity):
    if entity=='patient': return url_for('patients')
    if entity=='doctor': return url_for('doctors')
    if entity=='appointment': return url_for('appointments')
    return url_for('module',name={'medicine':'pharmacy','lab':'laboratory','bed':'beds','bill':'billing','ambulance':'ambulances'}[entity])

@app.route('/delete/<entity>/<int:record_id>',methods=['POST'])
@login_required
def delete_record(entity,record_id):
    model=ENTITY_MODELS.get(entity)
    if not model: flash('Invalid record type','error'); return redirect(url_for('dashboard'))
    record=db.session.get(model,record_id)
    if not record: flash('Record not found','error'); return redirect(entity_return_url(entity))
    try:
        db.session.delete(record); db.session.commit(); flash('Record deleted successfully','success')
    except Exception:
        db.session.rollback(); flash('This record is linked to other hospital records. Delete or reassign those linked records first.','error')
    return redirect(entity_return_url(entity))

def load_demo_data():
    db.create_all()
    admin=User.query.filter_by(email='admin@medicare.com').first()
    if not admin:
        db.session.add(User(name='Rajneesh Sharma',email='admin@medicare.com',password_hash=generate_password_hash('Admin@123'),role='admin'))
    else:
        admin.password_hash=generate_password_hash('Admin@123'); admin.active=True

    if Patient.query.count()==0:
        patients=[
            Patient(patient_code='PT-2841',name='Ananya Mehta',dob=date(1994,5,18),gender='Female',blood_group='A+',phone='9876501042',emergency_contact='Rakesh Mehta - 9810011223',address='Sector 70, Mohali',allergies='Penicillin',previous_diseases='Hypertension',insurance='Star Health - SH2841'),
            Patient(patient_code='PT-1967',name='Rohan Verma',dob=date(1987,11,3),gender='Male',blood_group='O+',phone='9876501967',emergency_contact='Neha Verma - 9810019670',address='Phase 7, Mohali',allergies='None',previous_diseases='Migraine',insurance='HDFC ERGO - HE1967'),
            Patient(patient_code='PT-3054',name='Kavya Sharma',dob=date(2001,2,14),gender='Female',blood_group='B+',phone='9876503054',emergency_contact='Ajay Sharma - 9810030540',address='Kharar, Punjab',allergies='Dust',previous_diseases='None',insurance='Ayushman Bharat'),
            Patient(patient_code='PT-2712',name='Ishaan Gupta',dob=date(2016,8,22),gender='Male',blood_group='AB+',phone='9876502712',emergency_contact='Priya Gupta - 9810027120',address='Sector 44, Chandigarh',allergies='Peanuts',previous_diseases='Asthma',insurance='Care Health - CH2712'),
            Patient(patient_code='PT-3088',name='Simran Kaur',dob=date(1978,6,9),gender='Female',blood_group='O-',phone='9876503088',emergency_contact='Harpreet Singh - 9810030880',address='Landran, Mohali',allergies='None',previous_diseases='Diabetes',insurance='ICICI Lombard - IL3088')]
        db.session.add_all(patients)

    if Doctor.query.count()==0:
        doctors=[
            Doctor(doctor_code='DR-001',name='Dr. Arjun Kapoor',department='Cardiology',qualification='MBBS, MD Cardiology',experience=14,fee=1200,phone='9876100001',available=True),
            Doctor(doctor_code='DR-002',name='Dr. Meera Joshi',department='Neurology',qualification='MBBS, DM Neurology',experience=11,fee=1400,phone='9876100002',available=True),
            Doctor(doctor_code='DR-003',name='Dr. Vikram Singh',department='Orthopedics',qualification='MBBS, MS Orthopedics',experience=16,fee=1000,phone='9876100003',available=True),
            Doctor(doctor_code='DR-004',name='Dr. Sana Khan',department='Pediatrics',qualification='MBBS, MD Pediatrics',experience=9,fee=800,phone='9876100004',available=True),
            Doctor(doctor_code='DR-005',name='Dr. Nitin Rao',department='General Medicine',qualification='MBBS, MD Medicine',experience=12,fee=900,phone='9876100005',available=False)]
        db.session.add_all(doctors)
    db.session.flush()

    if Appointment.query.count()==0:
        ps=Patient.query.order_by(Patient.id).all(); ds=Doctor.query.order_by(Doctor.id).all()
        db.session.add_all([
            Appointment(patient_id=ps[0].id,doctor_id=ds[0].id,appointment_date=date.today(),appointment_time=time(9,0),appointment_type='Online',reason='Chest discomfort',status='Confirmed',queue_number=1),
            Appointment(patient_id=ps[1].id,doctor_id=ds[1].id,appointment_date=date.today(),appointment_time=time(9,30),appointment_type='Walk-in',reason='Severe headache',status='In Progress',queue_number=2),
            Appointment(patient_id=ps[2].id,doctor_id=ds[2].id,appointment_date=date.today(),appointment_time=time(10,15),appointment_type='Online',reason='Knee pain',status='Waiting',queue_number=3),
            Appointment(patient_id=ps[3].id,doctor_id=ds[3].id,appointment_date=date.today(),appointment_time=time(11,0),appointment_type='Walk-in',reason='Routine checkup',status='Confirmed',queue_number=4)])

    if Medicine.query.count()==0:
        db.session.add_all([Medicine(name='Paracetamol 500mg',batch_no='PCM-1042',stock=4280,price=25,expiry_date=date.today()+timedelta(days=500),supplier='MedLife Pharma'),Medicine(name='Amoxicillin 250mg',batch_no='AMX-0871',stock=620,price=95,expiry_date=date.today()+timedelta(days=280),supplier='CureWell Labs'),Medicine(name='Insulin Glargine',batch_no='INS-1145',stock=84,price=740,expiry_date=date.today()+timedelta(days=35),supplier='HealthCore'),Medicine(name='Azithromycin 500mg',batch_no='AZI-0964',stock=1120,price=125,expiry_date=date.today()+timedelta(days=420),supplier='CureWell Labs')])
    if Bed.query.count()==0:
        beds=[]
        for ward,prefix,count,occupied in [('ICU','ICU',12,7),('General Ward','GW',20,11),('Private Room','PR',8,3),('Deluxe Room','DX',4,1)]:
            for i in range(1,count+1): beds.append(Bed(bed_number=f'{prefix}-{i:02d}',ward_type=ward,status='Occupied' if i<=occupied else 'Available'))
        db.session.add_all(beds)
    db.session.flush()
    ps=Patient.query.order_by(Patient.id).all()
    if LabTest.query.count()==0:
        db.session.add_all([LabTest(patient_id=ps[0].id,test_name='Complete Blood Count',test_date=date.today(),status='Processing',result='Awaiting report'),LabTest(patient_id=ps[1].id,test_name='MRI Brain',test_date=date.today(),status='Scheduled'),LabTest(patient_id=ps[2].id,test_name='ECG',test_date=date.today(),status='Report Ready',result='Normal sinus rhythm'),LabTest(patient_id=ps[3].id,test_name='Urine Routine',test_date=date.today(),status='Sample Due')])
    if Bill.query.count()==0:
        db.session.add_all([Bill(patient_id=ps[0].id,consultation=1200,medicine=1460,lab=2850,room=4000,discount=0,insurance_deduction=3000,payment_method='UPI',status='Pending'),Bill(patient_id=ps[1].id,consultation=1400,medicine=850,lab=4500,room=0,discount=250,insurance_deduction=1000,payment_method='Card',status='Paid')])
    if Ambulance.query.count()==0:
        db.session.add_all([Ambulance(vehicle_number='PB 65 AM 1042',driver_name='Raj Kumar',driver_phone='9876201001',ambulance_type='Advanced Life Support',status='Available'),Ambulance(vehicle_number='PB 65 BX 7721',driver_name='Amit Singh',driver_phone='9876201002',ambulance_type='Basic Life Support',status='On Duty'),Ambulance(vehicle_number='PB 65 CR 2088',driver_name='Deepak Verma',driver_phone='9876201003',ambulance_type='Patient Transport',status='Available')])
    db.session.commit()
    print('Demo data loaded successfully!')
    print('Admin login: admin@medicare.com / Admin@123')

@app.cli.command('seed')
def seed_command():
    """Manually reload any missing demonstration records."""
    load_demo_data()

if __name__=='__main__':
    with app.app_context():
        # Automatically creates the database and loads demo data on first run.
        # The loader checks existing tables, so records are not duplicated.
        load_demo_data()
    app.run(debug=True)
