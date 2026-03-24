from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email


class AdminLoginForm(FlaskForm):
    admin_email = EmailField("Admin Email", validators=[DataRequired(), Email()])
    admin_password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Admin Login")