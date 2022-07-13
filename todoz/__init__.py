import os
import sqlite3
import secrets
import datetime

from flask import Flask, g, redirect, render_template, session, url_for
from flask_debugtoolbar import DebugToolbarExtension
from flask_wtf.csrf import CSRFProtect


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    csfr = CSRFProtect(app=app)  # Sets up CSRF token validation globally
    app.config.from_mapping(
        SECRET_KEY=secrets.token_urlsafe(100),  # Change this when deploying to a random hash
        DATABASE=os.path.join(
            app.instance_path, "todoz.sqlite3"),  # Db location
        DEBUG_TB_INTERCEPT_REDIRECTS=False,
        PERMANENT_SESSION_LIFETIME = datetime.timedelta(minutes=5),
        PREFERRED_URL_SCHEME = "https",
    )

    toolbar = DebugToolbarExtension(app=app)
    if test_config is None:
        # Loads instance config when not testing from file
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/welcome")
    def index():
        if "username" not in session:
            return f"Welcome! Please login to continue"
        else:
            return f"Welcome to TodoZ user: {session.get('username').capitalize()}"

    from todoz import auth, db, forms, todoZ
    db.init_app(app)  # Register the database with application
    # Register the authentication blueprint
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(forms.contact_bp)
    app.register_blueprint(todoZ.task_bp)
    app.add_url_rule("/", endpoint="auth.login")

    return app
