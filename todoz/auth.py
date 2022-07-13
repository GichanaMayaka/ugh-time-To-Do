import functools

from flask import (Blueprint, flash, g, redirect, render_template, request,
                   session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from todoz.db import get_db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        username = request.form["username"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        db = get_db()
        errors = None

        if username is None:
            errors = "Username cannot be null"
        elif password is None:
            errors = "Password cannot be null"

        if errors is None:
            try:
                db.execute(
                    f"""
                        INSERT INTO users (name, username, email, phone, password)
                        VALUES (?,?,?,?,?)
                    """,
                    (name, username, email, phone, generate_password_hash(password))
                )
                db.commit()
            except db.IntegrityError:
                errors = f"User {username.capitalize()} is already registered"
            else:
                return redirect(url_for("task.create_task"))
        flash(errors)

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        errors = None
        user = db.execute(
            """SELECT * FROM users WHERE username = (?)""", (username,)
        ).fetchone()

        if user is None:
            errors = "You are not registered. Please proceed to the Registration screen"
        elif not check_password_hash(user["password"], password):
            errors = "Invalid Password"

        if errors is None:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = username
            return redirect(url_for("task.users_tasks"))

        flash(errors)

    return render_template("auth/login.html")


@auth_bp.before_app_first_request
def load_signed_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            """
                SELECT * FROM users WHERE username = ?
            """, (user_id,)
        ).fetchone()


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


def login_required(view):
    # Decorator to ensure one has authenticated to make changes
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
