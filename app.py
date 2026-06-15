import sqlite3
from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "hospital_secret"

def init_db():
    con = sqlite3.connect("hospital.db")

    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS patients(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        gender TEXT,
        phone TEXT,
        disease TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS doctors(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialization TEXT,
        phone TEXT,
        experience TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_name TEXT,
        doctor_name TEXT,
        appointment_date TEXT,
        status TEXT DEFAULT 'Pending'
    )
    """)

    try:
        cur.execute("ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'Pending'")
    except:
        pass

    con.commit()

    con.close()

@app.route("/")
def home():
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":
            session["admin"] = username
            return redirect("/dashboard")
        else:
            return "Invalid Username or Password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect("/login")

    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute("SELECT COUNT(*) FROM patients")
    patient_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM doctors")
    doctor_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM appointments")
    appointment_count = cur.fetchone()[0]

    con.close()

    return render_template(
        "dashboard.html",
        patient_count=patient_count,
        doctor_count=doctor_count,
        appointment_count=appointment_count
    )

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")
@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        disease = request.form["disease"]

        con = sqlite3.connect("hospital.db")
        cur = con.cursor()

        cur.execute("""
        INSERT INTO patients(name, age, gender, phone, disease)
        VALUES (?, ?, ?, ?, ?)
        """, (name, age, gender, phone, disease))

        con.commit()
        con.close()

        return """
        <script>
        alert('Patient Added Successfully');
        window.location.href='/patients';
        </script>
        """

    return render_template("add_patient.html")

@app.route("/patients")
def patients():

    search = request.args.get("search", "")

    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    if search:
        cur.execute(
            "SELECT * FROM patients WHERE name LIKE ?",
            ('%' + search + '%',)
        )
    else:
        cur.execute("SELECT * FROM patients")

    data = cur.fetchall()

    con.close()

    return render_template(
        "patients.html",
        patients=data,
        search=search
    )

@app.route("/edit_patient/<int:id>", methods=["GET", "POST"])
def edit_patient(id):
    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        phone = request.form["phone"]
        disease = request.form["disease"]

        cur.execute("""
        UPDATE patients
        SET name=?, age=?, gender=?, phone=?, disease=?
        WHERE id=?
        """, (name, age, gender, phone, disease, id))

        con.commit()
        con.close()

        return redirect("/patients")

    cur.execute("SELECT * FROM patients WHERE id=?", (id,))
    patient = cur.fetchone()

    con.close()

    return render_template("edit_patient.html", patient=patient)
@app.route("/delete_patient/<int:id>")
def delete_patient(id):

    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute("DELETE FROM patients WHERE id=?", (id,))

    con.commit()
    con.close()

    return redirect("/patients")
@app.route("/add_doctor", methods=["GET", "POST"])
def add_doctor():
    if request.method == "POST":
        name = request.form["name"]
        specialization = request.form["specialization"]
        phone = request.form["phone"]
        experience = request.form["experience"]

        con = sqlite3.connect("hospital.db")
        cur = con.cursor()

        cur.execute("""
        INSERT INTO doctors(name, specialization, phone, experience)
        VALUES (?, ?, ?, ?)
        """, (name, specialization, phone, experience))

        con.commit()
        con.close()

        return """
        <script>
        alert('Doctor Added Successfully');
        window.location.href='/doctors';
        </script>
        """

    return render_template("add_doctor.html")

@app.route("/doctors")
def doctors():
    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM doctors")
    data = cur.fetchall()

    con.close()

    return render_template("doctors.html", doctors=data)

@app.route("/book_appointment", methods=["GET", "POST"])
def book_appointment():
    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM patients")
    patients = cur.fetchall()

    cur.execute("SELECT * FROM doctors")
    doctors = cur.fetchall()

    if request.method == "POST":
        patient_name = request.form["patient_name"]
        doctor_name = request.form["doctor_name"]
        appointment_date = request.form["appointment_date"]

        cur.execute("""
            INSERT INTO appointments(patient_name, doctor_name, appointment_date, status)
            VALUES (?, ?, ?, ?)
            """, (patient_name, doctor_name, appointment_date, "Pending"))

        con.commit()
        con.close()

        return """
        <script>
        alert('Appointment Booked Successfully');
        window.location.href='/appointments';
        </script>
        """

    con.close()
    return render_template(
        "book_appointment.html",
        patients=patients,
        doctors=doctors
    )
@app.route("/appointments")
def appointments():
    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute("SELECT * FROM appointments")
    data = cur.fetchall()

    con.close()

    return render_template("appointments.html", appointments=data)

@app.route("/edit_doctor/<int:id>", methods=["GET", "POST"])
def edit_doctor(id):

    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    if request.method == "POST":

        name = request.form["name"]
        specialization = request.form["specialization"]
        phone = request.form["phone"]
        experience = request.form["experience"]

        cur.execute("""
        UPDATE doctors
        SET name=?, specialization=?, phone=?, experience=?
        WHERE id=?
        """, (name, specialization, phone, experience, id))

        con.commit()
        con.close()

        return redirect("/doctors")

    cur.execute(
        "SELECT * FROM doctors WHERE id=?",
        (id,)
    )

    doctor = cur.fetchone()

    con.close()

    return render_template(
        "edit_doctor.html",
        doctor=doctor
    )
@app.route("/delete_doctor/<int:id>")
def delete_doctor(id):

    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute(
        "DELETE FROM doctors WHERE id=?",
        (id,)
    )

    con.commit()
    con.close()

    return redirect("/doctors")

@app.route("/delete_appointment/<int:id>")
def delete_appointment(id):

    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute(
        "DELETE FROM appointments WHERE id=?",
        (id,)
    )

    con.commit()
    con.close()

    return redirect("/appointments")
@app.route("/approve_appointment/<int:id>")
def approve_appointment(id):
    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute(
        "UPDATE appointments SET status='Approved' WHERE id=?",
        (id,)
    )

    con.commit()
    con.close()

    return redirect("/appointments")


@app.route("/complete_appointment/<int:id>")
def complete_appointment(id):
    con = sqlite3.connect("hospital.db")
    cur = con.cursor()

    cur.execute(
        "UPDATE appointments SET status='Completed' WHERE id=?",
        (id,)
    )

    con.commit()
    con.close()

    return redirect("/appointments")


init_db()

if __name__ == "__main__":
    app.run(debug=True)