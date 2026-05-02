from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField,TextAreaField
from wtforms.validators import Optional,DataRequired,Length,Email


class HomeSearchForm(FlaskForm):
    type = SelectField(
        "Property Type",
        choices=[
            ("", "Choose type"),
            ("house", "House"),
            ("apartment", "Apartment"),
            ("land", "Land"),
            ("commercial", "Commercial"),
        ],
        validators=[]
    )

    location = StringField(
        "State / City",
        validators=[Optional()]
    )

    budget = SelectField(
        "Budget (₦)",
        choices=[
            ("", "Any"),
            ("under_20m", "Under ₦20M"),
            ("20m_50m", "₦20M – ₦50M"),
            ("50m_100m", "₦50M – ₦100M"),
            ("100m_plus", "₦100M+"),
        ],
        validators=[Optional()]
    )

    submit = SubmitField("Search Now")


class ContactForm(FlaskForm):
    fullname = StringField("Full Name", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email Address", validators=[DataRequired(), Email()])
    subject = StringField("Subject", validators=[DataRequired(), Length(min=3, max=150)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(min=10, max=2000)])
    submit = SubmitField("Send Message")