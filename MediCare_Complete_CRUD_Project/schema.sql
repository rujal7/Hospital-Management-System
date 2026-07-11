CREATE DATABASE IF NOT EXISTS medicare_hms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE medicare_hms;

CREATE TABLE IF NOT EXISTS users (
 id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100) NOT NULL,
 email VARCHAR(120) NOT NULL UNIQUE, password_hash VARCHAR(255) NOT NULL,
 role ENUM('admin','doctor','nurse','receptionist','patient') NOT NULL DEFAULT 'patient',
 active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patients (
 id INT AUTO_INCREMENT PRIMARY KEY, patient_code VARCHAR(20) UNIQUE,
 name VARCHAR(100) NOT NULL, dob DATE, gender VARCHAR(20), blood_group VARCHAR(5),
 phone VARCHAR(20), emergency_contact VARCHAR(120), address TEXT, allergies TEXT,
 previous_diseases TEXT, insurance VARCHAR(150), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doctors (
 id INT AUTO_INCREMENT PRIMARY KEY, doctor_code VARCHAR(20) UNIQUE, name VARCHAR(100) NOT NULL,
 department VARCHAR(80), qualification VARCHAR(120), experience INT DEFAULT 0,
 fee DECIMAL(10,2) DEFAULT 0, phone VARCHAR(20), available BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS appointments (
 id INT AUTO_INCREMENT PRIMARY KEY, patient_id INT NOT NULL, doctor_id INT NOT NULL,
 appointment_date DATE NOT NULL, appointment_time TIME NOT NULL, appointment_type VARCHAR(30),
 reason TEXT, status VARCHAR(30) DEFAULT 'Scheduled', queue_number INT,
 FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
 FOREIGN KEY(doctor_id) REFERENCES doctors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS medicines (
 id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(120) NOT NULL, batch_no VARCHAR(50),
 stock INT DEFAULT 0, price DECIMAL(10,2) DEFAULT 0, expiry_date DATE, supplier VARCHAR(120)
);

CREATE TABLE IF NOT EXISTS lab_tests (
 id INT AUTO_INCREMENT PRIMARY KEY, patient_id INT NOT NULL, test_name VARCHAR(100) NOT NULL,
 test_date DATE, status VARCHAR(30) DEFAULT 'Pending', report_file VARCHAR(255), result TEXT,
 FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS beds (
 id INT AUTO_INCREMENT PRIMARY KEY, bed_number VARCHAR(20) UNIQUE, ward_type VARCHAR(50),
 status VARCHAR(20) DEFAULT 'Available', patient_id INT NULL,
 FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS bills (
 id INT AUTO_INCREMENT PRIMARY KEY, patient_id INT NOT NULL, consultation DECIMAL(10,2) DEFAULT 0,
 medicine DECIMAL(10,2) DEFAULT 0, lab DECIMAL(10,2) DEFAULT 0, room DECIMAL(10,2) DEFAULT 0,
 surgery DECIMAL(10,2) DEFAULT 0, discount DECIMAL(10,2) DEFAULT 0,
 insurance_deduction DECIMAL(10,2) DEFAULT 0, payment_method VARCHAR(30), status VARCHAR(20) DEFAULT 'Pending',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS ambulances (
 id INT AUTO_INCREMENT PRIMARY KEY, vehicle_number VARCHAR(30) UNIQUE, driver_name VARCHAR(100),
 driver_phone VARCHAR(20), ambulance_type VARCHAR(80), status VARCHAR(30) DEFAULT 'Available'
);

