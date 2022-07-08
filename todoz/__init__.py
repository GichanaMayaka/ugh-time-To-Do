import os
import sqlite3

from flask import (Flask, g, session)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',  # Change this when deploying to a random hash
        DATABASE=os.path.join(
            app.instance_path, "todoz.sqlite3"),  # Db location
    )

    if test_config is None:
        # Loads instance config when not testing from file
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        return f"Welcome to TodoZ user Id: {session.get('user_id')}"

    from todoz import auth, db
    db.init_app(app)  # Register the database with application
    # Register the authentication blueprint
    app.register_blueprint(auth.auth_bp)

    return app
