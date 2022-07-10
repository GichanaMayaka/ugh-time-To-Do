from flask import Blueprint, g, redirect, render_template
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import (DateField, PasswordField, SelectField,
                     StringField, SubmitField, TextAreaField, TimeField)
from wtforms.validators import URL, DataRequired, EqualTo, Length, email


task_bp = Blueprint("task", __name__, url_prefix="task/")

@task_bp.route("/create-task", methods = ["GET", "POST"])
def create_task():