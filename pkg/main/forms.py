from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import Optional


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