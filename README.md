# MediCare Hospital Management System

Full-stack college project using Flask, MySQL, HTML and CSS.

## Setup in VS Code

1. Install Python 3.11+ (MySQL is optional).
2. Open the MediCare_Complete_CRUD_Project folder in VS Code.
3. Create a virtual environment:

        python -m venv venv

4. Activate it on Windows:

        venv\Scripts\activate

5. Install packages:

        pip install -r requirements.txt

6. (Optional, for MySQL) Copy .env.example to .env and enter your MySQL password.
7. (Optional, for MySQL) Create the database by running schema.sql in MySQL Workbench.
8. Start the project:

        python app.py

9. Open http://127.0.0.1:5000

Default login: admin@medicare.com / Admin@123

## Demo data loads automatically

If no MySQL settings are found, the app uses a local SQLite database. It creates the admin login, sample patients, doctors, appointments, medicines, lab tests, beds, bills and ambulances automatically.

## Live UI demo

https://rujal7.github.io/Hospital-Management-System/
