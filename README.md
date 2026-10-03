# MediCare Hospital Management System

Full-stack college project using Flask, MySQL, HTML and CSS.

## Setup in VS Code

1. Install Python 3.11+ and MySQL Server.
2. Open this folder in VS Code.
3. Create a virtual environment:
  
4. Activate it on Windows:
   `venv\\Scripts\\activate`
5. Install packages:
 
6. Copy `.env.example` to `.env` and enter your MySQL password.
7. Create the database by running `schema.sql` in MySQL Workbench.
8. Start the project:
  
9. Open `http://127.0.0.1:5000`

Default login: `admin@medicare.com` / `Admin@123`


Simply run `python app.py`. The program automatically creates the database,
admin login, sample patients, doctors, today's appointments, medicines, lab
tests, beds, bills and ambulances. It checks existing records first, so data is
not duplicated when you restart the program. The optional command
`python -m flask --app app seed` can still restore any missing demo section.
