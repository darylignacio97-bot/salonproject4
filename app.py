from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3, json
from pathlib import Path
from functools import wraps

BASE_DIR = Path(__file__).resolve().parent
DB_FILE = BASE_DIR / "salon.db"
OLD_JSON = BASE_DIR / "appointments.json"

app = Flask(__name__)
app.secret_key = "change-this-secret-key"

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

SERVICES = [
    ("Hair Cut", 350, "Professional haircut and styling"),
    ("Hair Color", 1200, "Hair coloring service"),
    ("Rebond", 1499, "Smooth and straight hair rebonding"),
    ("Manicure", 299, "Classic manicure and nail care"),
    ("Spa", 799, "Relaxing salon spa treatment"),
]

STAFF = [
    ("Maria Santos","Hair Stylist","09123456789"),
    ("Anna Cruz","Nail Technician","09234567890"),
    ("Jessica Garcia","Hair Colorist","09345678901"),
    ("Sofia Reyes","Beauty Specialist","09456789012"),
    ("Angela Flores","Hair Stylist","09567890123"),
    ("Patricia Ramos","Nail Technician","09678901234"),
    ("Catherine Lopez","Hair Colorist","09789012345"),
    ("Isabella Torres","Beauty Specialist","09890123456"),
    ("Michelle Aquino","Hair Stylist","09901234567"),
    ("Rachel Mendoza","Nail Technician","09012345678"),
]

PROMOS = [
    ("Rebond","₱1,499","Hair rebonding promo"),
    ("Manicure","₱299","Classic manicure promo"),
    ("Spa","₱799","Relaxing spa promo"),
]

def get_db():
    db = sqlite3.connect(DB_FILE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript("""
    CREATE TABLE IF NOT EXISTS services(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL, price REAL NOT NULL, description TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS staff(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, position TEXT NOT NULL, contact TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer TEXT NOT NULL, contact TEXT, date TEXT NOT NULL, time TEXT NOT NULL,
        service TEXT NOT NULL, staff TEXT NOT NULL, price REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Booked', created TEXT DEFAULT CURRENT_TIMESTAMP);
    """)
    for row in SERVICES:
        db.execute("INSERT OR IGNORE INTO services(name,price,description) VALUES(?,?,?)", row)
    if db.execute("SELECT COUNT(*) FROM staff").fetchone()[0] == 0:
        db.executemany("INSERT INTO staff(name,position,contact) VALUES(?,?,?)", STAFF)

    # Preserve existing appointments.json when it exists.
    if db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0] == 0 and OLD_JSON.exists():
        try:
            data = json.loads(OLD_JSON.read_text(encoding="utf-8"))
            prices = {x[0]: x[1] for x in SERVICES}
            for x in data if isinstance(data, list) else []:
                if isinstance(x, dict):
                    service = x.get("service", "Hair Cut")
                    db.execute("""INSERT INTO appointments
                    (customer,contact,date,time,service,staff,price,status)
                    VALUES(?,?,?,?,?,?,?,?)""", (
                        x.get("customer",""), x.get("contact",""), x.get("date",""),
                        x.get("time",""), service, x.get("staff", STAFF[0][0]),
                        float(x.get("price", prices.get(service,0)) or 0),
                        x.get("status","Booked")))
        except Exception:
            pass
     # Add appointment records until there are 100 total.
    # Existing appointments are preserved.
    appointment_count = db.execute(
        "SELECT COUNT(*) FROM appointments"
    ).fetchone()[0]

    if appointment_count < 100:
        customers = [
            "Juan Dela Cruz",
            "Maria Clara",
            "Ana Reyes",
            "Mark Santos",
            "Sofia Garcia",
            "John Cruz",
            "Angela Lopez",
            "Carlo Mendoza",
            "Jessica Torres",
            "Patrick Ramos",
        ]

        times = [
            "10:00 AM",
            "11:00 AM",
            "12:00 PM",
            "1:00 PM",
            "2:00 PM",
            "3:00 PM",
            "4:00 PM",
            "5:00 PM",
            "6:00 PM",
            "7:00 PM",
        ]

        services_data = db.execute(
            "SELECT name, price FROM services ORDER BY id"
        ).fetchall()

        staff_data = db.execute(
            "SELECT name FROM staff ORDER BY id"
        ).fetchall()

        needed = 100 - appointment_count

        for i in range(needed):
            service = services_data[i % len(services_data)]
            staff_name = staff_data[i % len(staff_data)]["name"]

            customer = customers[i % len(customers)]
            date = f"2026-10-{(i % 30) + 1:02d}"
            time = times[i % len(times)]

            db.execute("""
                INSERT INTO appointments
                (customer, contact, date, time, service, staff, price, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                customer,
                f"09{100000000 + i}",
                date,
                time,
                service["name"],
                staff_name,
                service["price"],
                "Booked"
            ))

    db.commit()
    db.close()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/", methods=["GET","POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        if request.form.get("email","").strip() == ADMIN_EMAIL and request.form.get("password","") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "error")
    return render_template("login.html")

@app.get("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.get("/dashboard")
@login_required
def dashboard():
    db = get_db()
    counts = {
        "appointments": db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0],
        "staff": db.execute("SELECT COUNT(*) FROM staff").fetchone()[0],
        "services": db.execute("SELECT COUNT(*) FROM services").fetchone()[0],
    }
    recent = db.execute("SELECT * FROM appointments ORDER BY id DESC LIMIT 5").fetchall()
    services = db.execute("SELECT * FROM services ORDER BY id").fetchall()
    db.close()
    return render_template("dashboard.html", counts=counts, recent=recent, services=services, promos=PROMOS)

@app.route("/appointments", methods=["GET","POST"])
@login_required
def appointments():
    db = get_db()
    services = db.execute("SELECT * FROM services ORDER BY id").fetchall()
    staff = db.execute("SELECT * FROM staff ORDER BY id").fetchall()
    if request.method == "POST":
        customer = request.form.get("customer","").strip()
        contact = request.form.get("contact","").strip()
        date = request.form.get("date","").strip()
        time = request.form.get("time","").strip()
        service = request.form.get("service","").strip()
        staff_name = request.form.get("staff","").strip()
        price = db.execute("SELECT price FROM services WHERE name=?", (service,)).fetchone()
        if not customer or not date or not time or not price:
            flash("Please complete the required fields.", "error")
        else:
            db.execute("""INSERT INTO appointments
            (customer,contact,date,time,service,staff,price,status)
            VALUES(?,?,?,?,?,?,?,'Booked')""",
            (customer,contact,date,time,service,staff_name,price["price"]))
            db.commit()
            db.close()
            flash("Appointment saved successfully.", "success")
            return redirect(url_for("appointments"))
    rows = db.execute("SELECT * FROM appointments ORDER BY id DESC").fetchall()
    db.close()
    return render_template("appointments.html", appointments=rows, services=services, staff=staff)

@app.get("/staff")
@login_required
def staff_page():
    db=get_db(); rows=db.execute("SELECT * FROM staff ORDER BY id").fetchall(); db.close()
    return render_template("staff.html", staff=rows)

@app.get("/services")
@login_required
def services_page():
    db=get_db(); rows=db.execute("SELECT * FROM services ORDER BY id").fetchall(); db.close()
    return render_template("services.html", services=rows, promos=PROMOS)

@app.get("/history")
@login_required
def history():
    db=get_db(); rows=db.execute("SELECT * FROM appointments ORDER BY id DESC").fetchall(); db.close()
    return render_template("history.html", appointments=rows)

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run(debug=True)
