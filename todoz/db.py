import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def init_app(app):
    # Cleanup with function (call function) close_db after returning request
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)  # adds command to CLI


def get_db():
    # Connect to database
    if 'db' not in g:
        g.db = sqlite3.connect(
            # Connects to db at file specified at the config["DATABASE"] location
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )

        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    # Close database connection
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


@click.command("init-db")
@with_appcontext
def init_db_command():
    init_db()
    click.echo("Database initialised successfully")
