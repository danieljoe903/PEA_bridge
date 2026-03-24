from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DecimalField, MultipleFileField, SubmitField
from wtforms.validators import DataRequired, Optional

class PropertyForm(FlaskForm):

    title = StringField(
        "Property Title",
        validators=[DataRequired()]
    )

    type = SelectField(
        "Property Type",
        choices=[
            ("house","House"),
            ("apartment","Apartment"),
            ("land","Land"),
            ("commercial","Commercial")
        ],
        validators=[DataRequired()]
    )

    address = TextAreaField(
        "Address",
        validators=[DataRequired()]
    )
    state=StringField('states',validators=[DataRequired(message='please fil in the state')])

    price = DecimalField(
        "Price",
        validators=[Optional()]
    )

    images = MultipleFileField("Property Images")

    submit = SubmitField("Add Property")