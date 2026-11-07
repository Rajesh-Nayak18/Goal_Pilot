import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-before-deployment")
DATABASE = "goal_pilot.db"

ROADMAPS = {
    "Web Developer": [
        ("Learn HTML, CSS and JavaScript", "Build the foundation of web development."),
        ("Create 3 mini projects", "Try a portfolio, calculator and to-do app."),
        ("Learn a frontend framework", "Start React after JavaScript basics."),
        ("Learn backend and databases", "Build APIs and connect a database."),
        ("Build portfolio and apply", "Publish projects and prepare for interviews.")
    ],
    "Data Analyst": [
        ("Learn Excel and SQL", "Practice formulas, filtering and SQL queries."),
        ("Learn Python basics", "Study Python, Pandas and NumPy."),
        ("Learn data visualization", "Try Power BI, Tableau or Matplotlib."),
        ("Complete 2 analysis projects", "Use real datasets and explain your findings."),
        ("Prepare your resume", "Create a portfolio and apply for internships.")
    ],
    "App Developer": [
        ("Learn programming basics", "Choose Kotlin for Android or Swift for iOS."),
        ("Learn UI design basics", "Practice layouts, navigation and usability."),
        ("Build a small app", "Create a notes or expense tracker app."),
        ("Connect APIs and database", "Store and retrieve app data."),
        ("Publish and apply", "Prepare a portfolio and apply for opportunities.")
    ]
}

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        goal TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL DEFAULT 'skill',
        due_date TEXT DEFAULT '',
        completed INTEGER NOT NULL DEFAULT 0,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    db.commit()
    db.close()

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return render_template("home.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6:
            flash("Username needs 3 characters and password needs 6 characters.")
            return render_template("auth.html", mode="Sign up")
        try:
            db = get_db()
            cur = db.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, generate_password_hash(password))
            )
            db.commit()
            session["user_id"] = cur.lastrowid
            session["username"] = username
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("That username is already taken.")
    return render_template("auth.html", mode="Sign up")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.")
    return render_template("auth.html", mode="Login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY completed ASC, id DESC",
        (session["user_id"],)
    ).fetchall()
    total = len(tasks)
    completed = sum(task["completed"] for task in tasks)
    progress = round(completed * 100 / total) if total else 0
    roadmap = ROADMAPS.get(user["goal"], [])
    return render_template(
        "dashboard.html", user=user, tasks=tasks, total=total,
        completed=completed, progress=progress, roadmap=roadmap,
        goals=list(ROADMAPS.keys())
    )

@app.route("/goal", methods=["POST"])
@login_required
def set_goal():
    goal = request.form.get("goal", "")
    if goal not in ROADMAPS:
        flash("Please select a valid goal.")
    else:
        get_db().execute(
            "UPDATE users SET goal = ? WHERE id = ?",
            (goal, session["user_id"])
        )
        get_db().commit()
        flash("Your roadmap has been updated.")
    return redirect(url_for("dashboard"))

@app.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title", "").strip()
    category = request.form.get("category", "skill")
    due_date = request.form.get("due_date", "")
    if not title:
        flash("Please enter a task name.")
    else:
        if category not in ("skill", "course", "project"):
            category = "skill"
        db = get_db()
        db.execute(
            "INSERT INTO tasks (user_id, title, category, due_date) VALUES (?, ?, ?, ?)",
            (session["user_id"], title, category, due_date)
        )
        db.commit()
        flash("Task added.")
    return redirect(url_for("dashboard"))

@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    db = get_db()
    task = db.execute(
        "SELECT completed FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    ).fetchone()
    if task:
        db.execute(
            "UPDATE tasks SET completed = ? WHERE id = ? AND user_id = ?",
            (0 if task["completed"] else 1, task_id, session["user_id"])
        )
        db.commit()
    return redirect(url_for("dashboard"))

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    db = get_db()
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    )
    db.commit()
    flash("Task deleted.")
    return redirect(url_for("dashboard"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
