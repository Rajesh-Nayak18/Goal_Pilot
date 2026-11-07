# Goal_Pilot

Goal Pilot — Starter Project

A beginner-friendly Flask + SQLite student goal and task tracker inspired by the uploaded Goal Pilot report.

## Features included
- Sign up and login (passwords are hashed)
- Choose a career goal
- Display a predefined learning roadmap
- Add, complete and delete tasks
- Optional due dates and task categories
- Dashboard progress percentage
- SQLite database created automatically

## 1. Install Python
Install Python 3.10 or newer. During Windows installation, tick **Add Python to PATH**.

## 2. Open this folder in VS Code
Open Terminal in VS Code and run:

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```cmd
venv\Scripts\activate.bat
```

## 3. Install packages

```bash
pip install -r requirements.txt
```

## 4. Run the app

```bash
python app.py
```

Open this address in your browser:

http://127.0.0.1:5000

Create an account and start using Goal Pilot. The `goal_pilot.db` database file is created automatically.

## Project structure

```text
goal_pilot_starter/
  app.py
  requirements.txt
  README.md
  goal_pilot.db       # created automatically after first run
  templates/
    base.html
    home.html
    auth.html
    dashboard.html
  static/
    style.css
```

## Development roadmap

1. **MVP (included):** authentication, career goal, roadmap, task manager and progress.
2. **Courses:** add Course and Subject tables; create course pages and connect study resources.
3. **Study library:** allow users to save links and upload PDFs safely.
4. **Planner:** add calendar view, deadlines and reminders.
5. **AI:** add a server-side Gemini API integration for task and resource suggestions. Keep the API key in an environment variable; never put it in JavaScript or commit it to Git.
6. **Testing:** test signup/login, invalid passwords, task creation, completion, deletion and user data isolation.
7. **Deployment:** deploy to a Python host such as Render or PythonAnywhere. Use a production secret key, HTTPS, persistent database storage and `debug=False`.

## Important security notes before public deployment
- Set a strong `SECRET_KEY` environment variable.
- Turn off Flask debug mode.
- Add CSRF protection to forms.
- Use HTTPS and persistent storage for SQLite, or move to PostgreSQL for a larger hosted app.
- Add file type/size checks before enabling uploads.
- Add rate limiting and account recovery before production use.

This is a working learning starter, not a copy of every advanced module shown in the report.
