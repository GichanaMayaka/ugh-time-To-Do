import datetime
import sqlite3
from turtle import title
from django.shortcuts import render

from flask import Blueprint, g, redirect, render_template, session, url_for, flash
from flask_wtf import FlaskForm, RecaptchaField
from werkzeug.exceptions import abort
from wtforms import DateTimeField, HiddenField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Length, email

from todoz.auth import login_required
from todoz.db import get_db

task_bp = Blueprint("task", __name__, url_prefix="/task")


# Create task Form definition
class CreateTaskForm(FlaskForm):
    title = StringField(
        label="Title",
        validators=[
            DataRequired(message="Please enter a title"),
            Length(
                min=2,
                message="Title is too short."
            ),
        ]
    )

    description = StringField(
        label="Description",
    )

    due_date = DateTimeField(
        label="Due Date",
        validators=[
            DataRequired(),
        ],
        default=datetime.datetime.utcnow(),
        format="%Y-%b-%d %H:%M %p"
    )

    user_id = HiddenField(
        label="user_id"
    )

    submit = SubmitField(label="Create Form")

    # def validate_on_submit(self):
    #     result = super(CreateTaskForm, self).validate_on_submit()
    #     if (self.due_date.strptime_format < datetime.datetime.today()):
    #         return False
    #     else:
    #         return True


class EditTaskForm(FlaskForm):
    title = StringField(
        label="Title",
        validators=[
            DataRequired(),
            Length(
                min=2,
                message="Title is too short"
            )
        ]
    )

    description = StringField(
        label="Description",
    )

    due_date = DateTimeField(
        label="Due Date",
        validators=[
            DataRequired(),
        ],
        default=datetime.datetime.utcnow(),
        format="%Y-%b-%d %H:%M %p"
    )

    task_id = HiddenField(
        label="task_id"
    )

    submit = SubmitField(label="Edit Form")


# Actual routing configuration for create-task view
@task_bp.route("/create-task", methods=["GET", "POST"])
@login_required
def create_task():
    task = CreateTaskForm()
    db = get_db()
    if task.validate_on_submit():
        try:
            db.execute(
                """
                    INSERT INTO tasks (user_id, title, description, due_date)
                    VALUES ( (SELECT id as user_id FROM users WHERE id = ?), ?, ?, ? )
                """, (session.get("user_id"), str(task.title.data), str(task.description.data), str(task.due_date.data))
            )
            db.commit()
            return redirect(url_for("task.create_task"))
        except db.IntegrityError:
            print("task not submitted")
            db.rollback()

    return render_template(
        "todo/create_task.html",
        task=task,
    )


def get_task(task_id, user_id):
    task = get_db().execute(
        """
            SELECT u.id as user_id, t.* 
                FROM tasks t INNER JOIN users u ON t.user_id = u.id
                    WHERE task_id = ?
                        AND u.id = ?
        """, (task_id, user_id,)
    ).fetchone()

    if task is None:
        abort(404, "Task does not exist")

    if task["user_id"] != user_id:
        abort(403, "You did not create this task...")

    return task


@task_bp.route("/<int:id>/edit-task", methods=["GET", "POST"])
@login_required
def edit_task(id):
    db = get_db()
    task = get_task(task_id=id, user_id=session.get("user_id"))
    edit_form = EditTaskForm(
        title=task["title"], description=task["description"],
        due_date=datetime.datetime.strptime(
            task["due_date"], "%Y-%m-%d %H:%M:%S"),
        task_id=task["task_id"]
    )

    if edit_form.validate_on_submit():
        try:
            db.execute(
                """
                    UPDATE tasks SET title = ?, description = ?, due_date = ?
                    WHERE task_id = ? AND user_id = (SELECT id FROM users WHERE id = ?)
                """, (str(edit_form.title.data), str(edit_form.description.data),
                      str(edit_form.due_date.data), int(task["task_id"]),
                      int(task["user_id"]),)
            )
            db.commit()
        except Exception:
            db.rollback()
        return redirect(url_for("task.create_task"))

    return render_template(
        "todo/edit_task.html",
        edit_form=edit_form
    )


@task_bp.route("/tasks", methods=["GET", "POST"])
@login_required
def users_tasks():
    user_id = session.get("user_id")
    try:
        db = get_db()
        active_tasks = db.execute(
            """
                SELECT * FROM tasks 
                WHERE user_id = ?
                AND due_date >= DATETIME('now')
                ORDER BY due_date desc
            """, (user_id,)
        ).fetchall()
        expired_tasks = db.execute(
            """
                SELECT * FROM tasks
                WHERE user_id = ?
                AND due_date < DATETIME('now')
                ORDER BY due_date desc
            """, (user_id,)
        ).fetchall()
    except db.OperationalError as error:
        flash(str(error))
        return redirect(url_for("task.create_task"))

    return render_template("todo/all_tasks.html", active_tasks=active_tasks, expired_tasks=expired_tasks)

@task_bp.route("/delete/<int:id>", methods=["GET"])
@login_required
def delete_task(id):
    try:
        db = get_db()
        db.execute(
            """
                DELETE FROM tasks WHERE task_id = ?
            """,(id,)
        )
        db.commit()
        return redirect(url_for("task.users_tasks"))
    except Exception as e:
        flash(str(e))
        db.rollback()
        return redirect(url_for("task.users_tasks"))