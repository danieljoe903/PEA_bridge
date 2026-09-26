from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

from flask_wtf import FlaskForm

from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    DecimalField,
    SubmitField
)

from flask_wtf.file import (
    MultipleFileField,
    FileAllowed
)

from wtforms.validators import (
    DataRequired,
    Length,
    Optional,
    NumberRange
)



class AdminLoginForm(FlaskForm):
    admin_email = EmailField("Admin Email", validators=[DataRequired(), Email()])
    admin_password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Admin Login")




class PropertyForm(FlaskForm):

    title = StringField(
        "Property Title",
        validators=[
            DataRequired(
                message="Please enter a property title."
            ),
            Length(
                min=5,
                max=300
            )
        ]
    )


    description = TextAreaField(
        "Property Description",
        validators=[
            DataRequired(
                message="Please enter a property description."
            ),
            Length(
                min=20,
                max=3000
            )
        ]
    )


    type = SelectField(
        "Property Type",
        choices=[
            ("house", "House"),
            ("apartment", "Apartment"),
            ("land", "Land"),
            ("commercial", "Commercial")
        ],
        validators=[
            DataRequired()
        ]
    )


    address = TextAreaField(
        "Property Address",
        validators=[
            DataRequired(
                message="Please enter the property address."
            )
        ]
    )


    state = StringField(
        "State",
        validators=[
            DataRequired(
                message="Please enter the state."
            )
        ]
    )


    price = DecimalField(
        "Price",
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Price must be a positive number."
            )
        ]
    )


    images = MultipleFileField(
        "Property Images",
        validators=[
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )
        ]
    )


    submit = SubmitField(
        "Publish Property"
    )