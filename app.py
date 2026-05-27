#!/usr/bin/env python3
"""
Simple URL-shortener SaaS (free tier + premium tier)
"""

import os
import string
import random
import datetime
from functools import wraps

from flask import (
    Flask, request, redirect, url_for,
    render_template_string, session, g, abort, flash
)
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(APP_ROOT, "shortener.db")
SECRET_KEY = os.environ.get("FLASK_SECRET", "dev-secret-key")
FREE_LINK_LIMIT = 5
FREE_CLICK_LIMIT = 100

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_KEY


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with app.open_resource("schema.sql", mode="r") as f:
        db.executescript(f.read())
    db.commit()


def random_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if "user_id" not in session:
            return redirect(url_for("login", next=request.path))
        return view(**kwargs)
    return wrapped_view


def current_user():
    uid = session.get("user_id")
    if uid is None:
        return None
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()


def month_start():
    now = datetime.datetime.utcnow()
    return datetime.datetime(now.year, now.month, 1)


HOME_TEMPLATE = """
<!doctype html>
<title>MiniURL – Home</title>
<h1>MiniURL – Simple URL Shortener</h1>
{% if user %}
  <p>Welcome, {{ user['email'] }}! (<a href="{{ url_for('logout') }}">log out</a>)</p>
  <p>Plan: {{ 'Premium' if user['is_premium'] else 'Free' }}</p>
  <p><a href="{{ url_for('dashboard') }}">Your dashboard</a></p>
{% else %}
  <p><a href="{{ url_for('login') }}">Log in</a> or <a href="{{ url_for('register') }}">register</a></p>
{% endif %}
"""

REGISTER_TEMPLATE = """
<!doctype html>
<title>Register</title>
<h1>Register</h1>
<form method="post">
  Email: <input type="email" name="email" required><br>
  Password: <input type="password" name="password" required><br>
  <button type="submit">Create account</button>
</form>
<p>Already have an account? <a href="{{ url_for('login') }}">Log in</a></p>
"""

LOGIN_TEMPLATE = """
<!doctype html>
<title>Login</title>
<h1>Login</h1>
<form method="post">
  Email: <input type="email" name="email" required><br>
  Password: <input type="password" name="password" required><br>
  <button type="submit">Log in</button>
</form>
<p>New user? <a href="{{ url_for('register') }}">Register here</a></p>
"""

DASHBOARD_TEMPLATE = """
<!doctype html>
<title>Dashboard</title>
<h1>Your Links</h1>
<p>Plan: {{ 'Premium' if user['is_premium'] else 'Free' }}</p>
{% if not user['is_premium'] %}
  <p>Free tier: {{ link_count }}/{{ free_limit }} links this month.</p>
  <p><a href="{{ url_for('upgrade') }}">Upgrade to Premium</a></p>
{% endif %}
<table border="1" cellpadding="5">
  <tr><th>Short URL</th><th>Target</th><th>Clicks</th><th>Created</th></tr>
  {% for link in links %}
    <tr>
      <td><a href="{{ url_for('redirect_short', code=link['code'], _external=True) }}">{{ request.host_url }}{{ link['code'] }}</a></td>
      <td>{{ link['target'] }}</td>
      <td>{{ link['clicks'] }}</td>
      <td>{{ link['created_at'][:10] }}</td>
    </tr>
  {% endfor %}
</table>

<h2>Create a new short link</h2>
<form method="post" action="{{ url_for('create') }}">
  Long URL: <input type="url" name="target" required size="60"><br>
  <button type="submit">Shorten</button>
</form>

<p><a href="{{ url_for('home') }}">← Back to home</a></p>
"""

UPGRADE_TEMPLATE = """
<!doctype html>
<title>Upgrade</title>
<h1>Upgrade to Premium</h1>
<p>In a real product you would be redirected to a payment gateway (Stripe, PayPal, …).</p>
<form method="post">
  <button type="submit">Simulate payment – become Premium now</button>
</form>
<p><a href="{{ url_for('dashboard') }}">← Back to dashboard</a></p>
"""


@app.route("/")
def home():
    return render_template_string(HOME_TEMPLATE, user=current_user())


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        db = get_db()
        if db.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            flash("Email already registered.", "error")
            return redirect(url_for("register"))
        db.execute(
            "INSERT INTO users (email, password_hash, is_premium) VALUES (?, ?, 0)",
            (email, generate_password_hash(password)),
        )
        db.commit()
        flash("Account created – please log in.", "info")
        return redirect(url_for("login"))
    return render_template_string(REGISTER_TEMPLATE)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            next_page = request.args.get("next") or url_for("dashboard")
            return redirect(next_page)
        flash("Invalid credentials.", "error")
    return render_template_string(LOGIN_TEMPLATE)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    db = get_db()
    links = db.execute(
        "SELECT * FROM links WHERE user_id = ? ORDER BY created_at DESC", (user["id"],)
    ).fetchall()
    month_start_ts = month_start().isoformat()
    link_count = db.execute(
        "SELECT COUNT(*) FROM links WHERE user_id = ? AND created_at >= ?",
        (user["id"], month_start_ts),
    ).fetchone()[0]
    return render_template_string(
        DASHBOARD_TEMPLATE,
        user=user,
        links=links,
        request=request,
        free_limit=FREE_LINK_LIMIT,
        link_count=link_count,
    )


@app.route("/create", methods=["POST"])
@login_required
def create():
    target = request.form["target"].strip()
    if not (target.startswith("http://") or target.startswith("https://")):
        flash("Please provide a full URL (including http/https).", "error")
        return redirect(url_for("dashboard"))

    user = current_user()
    db = get_db()

    if not user["is_premium"]:
        month_start_ts = month_start().isoformat()
        link_count = db.execute(
            "SELECT COUNT(*) FROM links WHERE user_id = ? AND created_at >= ?",
            (user["id"], month_start_ts),
        ).fetchone()[0]
        if link_count >= FREE_LINK_LIMIT:
            flash("Free tier limit reached – upgrade to create more links.", "error")
            return redirect(url_for("dashboard"))

    while True:
        code = random_code()
        if not db.execute("SELECT 1 FROM links WHERE code = ?", (code,)).fetchone():
            break

    db.execute(
        "INSERT INTO links (user_id, code, target, clicks, created_at) VALUES (?, ?, ?, 0, ?)",
        (user["id"], code, target, datetime.datetime.utcnow().isoformat()),
    )
    db.commit()
    return redirect(url_for("dashboard"))


@app.route("/upgrade", methods=["GET", "POST"])
@login_required
def upgrade():
    if request.method == "POST":
        db = get_db()
        db.execute("UPDATE users SET is_premium = 1 WHERE id = ?", (current_user()["id"],))
        db.commit()
        return redirect(url_for("dashboard"))
    return render_template_string(UPGRADE_TEMPLATE)


@app.route("/<code>")
def redirect_short(code):
    db = get_db()
    link = db.execute("SELECT * FROM links WHERE code = ?", (code,)).fetchone()
    if not link:
        abort(404, description="Short link not found")

    user = db.execute("SELECT * FROM users WHERE id = ?", (link["user_id"],)).fetchone()
    if not user["is_premium"] and link["clicks"] >= FREE_CLICK_LIMIT:
        abort(403, description="Free click limit exceeded – upgrade to continue using this link")

    db.execute("UPDATE links SET clicks = clicks + 1 WHERE id = ?", (link["id"],))
    db.commit()
    return redirect(link["target"])


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)
