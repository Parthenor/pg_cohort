import os
import heapq
import sqlite3
from functools import wraps
from pathlib import Path
from urllib.parse import urlparse

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# Set FLASK_SECRET_KEY before deployment. The fallback is only for local coursework demos.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "local-only-change-this-key-before-deployment")
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "pg_cohort.db"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            college TEXT NOT NULL,
            gender TEXT NOT NULL,
            city TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS pg_accommodations (
            pg_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pg_name TEXT NOT NULL,
            location TEXT NOT NULL,
            monthly_rent INTEGER NOT NULL CHECK(monthly_rent >= 0),
            room_type TEXT NOT NULL,
            facilities TEXT NOT NULL,
            available_beds INTEGER NOT NULL DEFAULT 1 CHECK(available_beds >= 0),
            distance_km REAL NOT NULL DEFAULT 0 CHECK(distance_km >= 0),
            description TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS roommate_preferences (
            preference_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL UNIQUE,
            budget INTEGER NOT NULL CHECK(budget >= 0),
            sleep_schedule TEXT NOT NULL,
            study_style TEXT NOT NULL,
            cleanliness TEXT NOT NULL,
            smoking_preference TEXT NOT NULL,
            preferred_location TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            pg_id INTEGER NOT NULL,
            request_date TEXT NOT NULL DEFAULT (date('now')),
            status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Approved', 'Rejected')),
            message TEXT DEFAULT '',
            FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE CASCADE,
            FOREIGN KEY(pg_id) REFERENCES pg_accommodations(pg_id) ON DELETE CASCADE
        );
        """)
        # Safe migration: add password_hash only if this existing database lacks it.
        columns = {row[1] for row in db.execute("PRAGMA table_info(students)").fetchall()}
        if "password_hash" not in columns:
            db.execute("ALTER TABLE students ADD COLUMN password_hash TEXT")

        if db.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
            db.executemany("INSERT INTO students(full_name,email,college,gender,city) VALUES(?,?,?,?,?)", [
                ("Aarav Sharma", "aarav@example.com", "North City University", "Male", "Delhi"),
                ("Kabir Mehta", "kabir@example.com", "North City University", "Male", "Delhi"),
                ("Riya Verma", "riya@example.com", "Metro Institute", "Female", "Delhi"),
                ("Ishaan Kapoor", "ishaan@example.com", "North City University", "Male", "Delhi"),
                ("Ananya Singh", "ananya@example.com", "Metro Institute", "Female", "Noida"),
            ])
            db.executemany("""INSERT INTO roommate_preferences
                (student_id,budget,sleep_schedule,study_style,cleanliness,smoking_preference,preferred_location)
                VALUES(?,?,?,?,?,?,?)""", [
                (1, 12000, "Early", "Quiet", "High", "Non-smoking", "North Campus"),
                (2, 11000, "Late", "Group", "Medium", "Non-smoking", "North Campus"),
                (3, 14000, "Early", "Quiet", "High", "Non-smoking", "South Campus"),
                (4, 12500, "Early", "Quiet", "Medium", "Non-smoking", "North Campus"),
                (5, 9000, "Late", "Quiet", "High", "Non-smoking", "Noida Sector 62"),
            ])
        if db.execute("SELECT COUNT(*) FROM pg_accommodations").fetchone()[0] == 0:
            db.executemany("""INSERT INTO pg_accommodations
                (pg_name,location,monthly_rent,room_type,facilities,available_beds,distance_km,description)
                VALUES(?,?,?,?,?,?,?,?)""", [
                ("Campus Nest PG", "North Campus", 11000, "Twin Sharing", "Wi-Fi, Meals, Laundry", 3, 0.8, "Student-friendly PG close to campus with meals and Wi-Fi."),
                ("Green View Residence", "North Campus", 12500, "Single Room", "Wi-Fi, Laundry, CCTV", 2, 1.4, "Quiet residence with study-friendly common areas."),
                ("Metro Stay", "South Campus", 9500, "Twin Sharing", "Wi-Fi, Meals", 4, 2.2, "Budget accommodation with essential facilities."),
                ("Urban Student House", "Noida Sector 62", 8500, "Triple Sharing", "Wi-Fi, Meals, Security", 5, 1.1, "Affordable rooms near the Noida education and office hub."),
                ("Scholar's Corner", "North Campus", 14000, "Single Room", "Wi-Fi, Meals, Laundry, CCTV", 1, 0.5, "Premium single rooms with convenient campus access."),
            ])



# Demonstration road network: distances are illustrative sample values (km),
# not live navigation data. Dijkstra requires non-negative edge weights.
CAMPUS_GRAPH = {
    "North Campus": [("University Road", 1.2), ("Central Junction", 2.0)],
    "South Campus": [("Central Junction", 2.4), ("South Avenue", 1.0)],
    "Noida Sector 62": [("Tech Park Road", 1.1)],
    "University Road": [("North Campus", 1.2), ("Central Junction", 1.0)],
    "Central Junction": [("North Campus", 2.0), ("University Road", 1.0), ("South Campus", 2.4), ("Market Circle", 1.3), ("Tech Park Road", 3.0)],
    "South Avenue": [("South Campus", 1.0), ("Market Circle", 1.8)],
    "Market Circle": [("Central Junction", 1.3), ("South Avenue", 1.8), ("Tech Park Road", 2.2)],
    "Tech Park Road": [("Noida Sector 62", 1.1), ("Central Junction", 3.0), ("Market Circle", 2.2)],
}

def dijkstra_shortest_paths(graph, start):
    """Return shortest distances and paths from start using Dijkstra's algorithm."""
    distances = {node: float("inf") for node in graph}
    previous = {node: None for node in graph}
    distances[start] = 0
    priority_queue = [(0, start)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)
        if current_distance > distances[current_node]:
            continue
        for neighbour, edge_weight in graph[current_node]:
            new_distance = current_distance + edge_weight
            if new_distance < distances[neighbour]:
                distances[neighbour] = new_distance
                previous[neighbour] = current_node
                heapq.heappush(priority_queue, (new_distance, neighbour))

    paths = {}
    for node in graph:
        if distances[node] == float("inf"):
            paths[node] = []
            continue
        path = []
        current = node
        while current is not None:
            path.append(current)
            current = previous[current]
        paths[node] = list(reversed(path))
    return distances, paths


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("student_id"):
            flash("Please log in to use that feature.", "error")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def roommate_matches(student_id):
    with get_db() as db:
        me = db.execute("""SELECT s.student_id, s.full_name, s.college, s.city, p.*
            FROM students s JOIN roommate_preferences p ON s.student_id = p.student_id
            WHERE s.student_id = ?""", (student_id,)).fetchone()
        if not me:
            return []
        others = db.execute("""SELECT s.student_id, s.full_name, s.college, s.city, p.*
            FROM students s JOIN roommate_preferences p ON s.student_id = p.student_id
            WHERE s.student_id != ?""", (student_id,)).fetchall()
    results = []
    for other in others:
        score, reasons = 0, []
        difference = abs(me["budget"] - other["budget"])
        budget_score = max(0, 30 - int(difference / 500) * 5)
        score += budget_score
        if budget_score >= 20:
            reasons.append("similar budget")
        for field, points, label in [
            ("sleep_schedule", 20, "sleep schedule"), ("study_style", 20, "study style"),
            ("cleanliness", 15, "cleanliness preference"),
            ("smoking_preference", 10, "smoking preference"),
            ("preferred_location", 5, "preferred location")]:
            if me[field] == other[field]:
                score += points
                reasons.append(label)
        results.append({"student_id": other["student_id"], "full_name": other["full_name"],
            "college": other["college"], "budget": other["budget"],
            "location": other["preferred_location"], "score": min(score, 100), "reasons": reasons})
    return sorted(results, key=lambda x: x["score"], reverse=True)


@app.route("/")
def home():
    with get_db() as db:
        pg_count = db.execute("SELECT COUNT(*) FROM pg_accommodations").fetchone()[0]
        student_count = db.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        booking_count = db.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        pgs = db.execute("SELECT * FROM pg_accommodations ORDER BY distance_km LIMIT 3").fetchall()
    return render_template("index.html", pg_count=pg_count, student_count=student_count, booking_count=booking_count, pgs=pgs)


@app.route("/register", methods=["GET", "POST"])
def register():
    if session.get("student_id"):
        return redirect(url_for("profile"))
    if request.method == "POST":
        name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        college = request.form.get("college", "").strip()
        gender = request.form.get("gender", "").strip()
        city = request.form.get("city", "").strip()
        budget_raw = request.form.get("budget", "").strip()
        sleep = request.form.get("sleep_schedule", "")
        study = request.form.get("study_style", "")
        clean = request.form.get("cleanliness", "")
        smoking = request.form.get("smoking_preference", "")
        location = request.form.get("preferred_location", "").strip()
        if not all([name, email, password, college, gender, city, budget_raw, sleep, study, clean, smoking, location]):
            flash("Please complete every required field.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
        elif not budget_raw.isdigit() or int(budget_raw) < 0:
            flash("Enter a valid monthly budget.", "error")
        else:
            try:
                with get_db() as db:
                    cur = db.execute("""INSERT INTO students(full_name,email,college,gender,city,password_hash)
                        VALUES(?,?,?,?,?,?)""", (name, email, college, gender, city, generate_password_hash(password)))
                    student_id = cur.lastrowid
                    db.execute("""INSERT INTO roommate_preferences
                        (student_id,budget,sleep_schedule,study_style,cleanliness,smoking_preference,preferred_location)
                        VALUES(?,?,?,?,?,?,?)""", (student_id, int(budget_raw), sleep, study, clean, smoking, location))
                session.clear()
                session["student_id"] = student_id
                flash("Account created! Your profile and roommate preferences have been saved.", "success")
                return redirect(url_for("profile"))
            except sqlite3.IntegrityError:
                flash("An account with that email already exists. Please log in instead.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("student_id"):
        return redirect(url_for("profile"))
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            student = db.execute("SELECT student_id, password_hash FROM students WHERE email = ?", (email,)).fetchone()
        if student and student["password_hash"] and check_password_hash(student["password_hash"], password):
            session.clear()
            session["student_id"] = student["student_id"]
            flash("You are now logged in.", "success")
            target = request.args.get("next", "")
            # Only allow a local path; never redirect to an external site.
            if target.startswith("/") and not target.startswith("//") and urlparse(target).netloc == "":
                return redirect(target)
            return redirect(url_for("profile"))
        flash("Email or password is incorrect. Older demo profiles cannot log in until registered with a password.", "error")
    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))


@app.route("/profile")
@login_required
def profile():
    with get_db() as db:
        student = db.execute("""SELECT s.student_id,s.full_name,s.email,s.college,s.gender,s.city,
            p.budget,p.sleep_schedule,p.study_style,p.cleanliness,p.smoking_preference,p.preferred_location
            FROM students s LEFT JOIN roommate_preferences p ON s.student_id=p.student_id
            WHERE s.student_id=?""", (session["student_id"],)).fetchone()
    if not student:
        session.clear()
        return redirect(url_for("login"))
    return render_template("profile.html", student=student)


@app.route("/pgs")
def pgs():
    location = request.args.get("location", "").strip()
    max_rent = request.args.get("max_rent", "").strip()
    query = "SELECT * FROM pg_accommodations WHERE available_beds > 0"
    params = []
    if location:
        query += " AND location LIKE ?"
        params.append(f"%{location}%")
    if max_rent.isdigit():
        query += " AND monthly_rent <= ?"
        params.append(int(max_rent))
    query += " ORDER BY monthly_rent ASC"
    with get_db() as db:
        listings = db.execute(query, params).fetchall()
    return render_template("pgs.html", listings=listings, location=location, max_rent=max_rent)



@app.route("/routes")
def routes():
    campuses = ["North Campus", "South Campus", "Noida Sector 62"]
    start = request.args.get("start", "North Campus")
    if start not in campuses:
        start = "North Campus"
    distances, paths = dijkstra_shortest_paths(CAMPUS_GRAPH, start)
    with get_db() as db:
        listings = db.execute("SELECT * FROM pg_accommodations ORDER BY pg_name").fetchall()
    results = []
    for pg in listings:
        destination = pg["location"]
        distance = distances.get(destination, float("inf"))
        results.append({
            "pg": pg,
            "distance": distance,
            "reachable": distance != float("inf"),
            "path": paths.get(destination, []),
        })
    results.sort(key=lambda item: item["distance"])
    return render_template("routes.html", campuses=campuses, start=start, results=results)


@app.route("/roommates")
@login_required
def roommates():
    with get_db() as db:
        me = db.execute("SELECT full_name FROM students WHERE student_id=?", (session["student_id"],)).fetchone()
    matches = roommate_matches(session["student_id"])
    return render_template("roommates.html", selected_name=me["full_name"] if me else "You", matches=matches)


@app.route("/book/<int:pg_id>", methods=["GET", "POST"])
@login_required
def book(pg_id):
    with get_db() as db:
        pg = db.execute("SELECT * FROM pg_accommodations WHERE pg_id = ?", (pg_id,)).fetchone()
        if not pg:
            flash("That PG listing was not found.", "error")
            return redirect(url_for("pgs"))
        if request.method == "POST":
            message = request.form.get("message", "").strip()
            if pg["available_beds"] < 1:
                flash("No beds are currently available.", "error")
            else:
                db.execute("INSERT INTO bookings(student_id, pg_id, message) VALUES(?,?,?)", (session["student_id"], pg_id, message))
                db.commit()
                flash("Booking request submitted successfully (demo).", "success")
                return redirect(url_for("bookings"))
    return render_template("book.html", pg=pg)


@app.route("/bookings")
@login_required
def bookings():
    with get_db() as db:
        rows = db.execute("""SELECT b.booking_id,b.request_date,b.status,b.message,
            s.full_name,p.pg_name,p.location,p.monthly_rent
            FROM bookings b JOIN students s ON b.student_id=s.student_id
            JOIN pg_accommodations p ON b.pg_id=p.pg_id
            WHERE b.student_id=? ORDER BY b.booking_id DESC""", (session["student_id"],)).fetchall()
    return render_template("bookings.html", bookings=rows)


@app.route("/schema")
def schema():
    return render_template("schema.html")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
