from flask_wtf import FlaskForm
from flask_wtf.file import (
    FileAllowed,
    FileRequired
)

from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    DecimalField,
    MultipleFileField,
    BooleanField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional
)


class LandlordPropertyForm(FlaskForm):

    # =========================
    # LANDLORD INFORMATION
    # =========================

    landlord_name = StringField(
        "Full Name",
        validators=[
            DataRequired(
                message="Please enter your full name."
            ),
            Length(
                min=2,
                max=150
            )
        ]
    )

    landlord_email = StringField(
        "Email Address",
        validators=[
            DataRequired(
                message="Please enter your email address."
            ),
            Email(
                message="Please enter a valid email address."
            ),
            Length(max=255)
        ]
    )

    landlord_phone = StringField(
        "Phone / WhatsApp Number",
        validators=[
            DataRequired(
                message="Please enter your phone number."
            ),
            Length(
                min=7,
                max=30
            )
        ]
    )

    # =========================
    # PROPERTY INFORMATION
    # =========================

    property_title = StringField(
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

    property_type = SelectField(
        "Property Type",
        choices=[
            ("", "Select property type"),
            ("house", "House"),
            ("apartment", "Apartment"),
            ("land", "Land"),
            ("commercial", "Commercial")
        ],
        validators=[
            DataRequired(
                message="Please select a property type."
            )
        ]
    )

    listing_type = SelectField(
    "Listing Purpose",
    choices=[
        ("", "Select listing purpose"),
        ("sale", "For Sale"),
        ("rent", "For Rent")
    ],
    validators=[
        DataRequired(
            message="Please select whether the property is for sale or rent."
        )
    ]
    )

    state = StringField(
        "State",
        validators=[
            DataRequired(
                message="Please enter the state."
            ),
            Length(max=100)
        ]
    )

    address = TextAreaField(
        "Property Address",
        validators=[
            DataRequired(
                message="Please enter the property address."
            ),
            Length(
                min=5,
                max=1000
            )
        ]
    )

    price = DecimalField(
        "Asking Price",
        places=2,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="Price cannot be negative."
            )
        ]
    )

    description = TextAreaField(
        "Property Description",
        validators=[
            DataRequired(
                message="Please describe the property."
            ),
            Length(
                min=20,
                max=3000,
                message=(
                    "Property description must be "
                    "between 20 and 3000 characters."
                )
            )
        ]
    )

    # =========================
    # PROPERTY IMAGES
    # =========================

    images = MultipleFileField(
        "Property Images",
        validators=[
            FileRequired(
                message="Please upload property images."
            ),
            FileAllowed(
                ["jpg", "jpeg", "png", "webp"],
                message=(
                    "Only JPG, JPEG, PNG and WEBP "
                    "images are allowed."
                )
            )
        ]
    )

    # =========================
    # DECLARATION
    # =========================

    declaration = BooleanField(
        (
            "I confirm that I am the property owner "
            "or I have authority to submit this property "
            "for marketing."
        ),
        validators=[
            DataRequired(
                message=(
                    "You must confirm that you have "
                    "authority to submit this property."
                )
            )
        ]
    )

    submit = SubmitField(
        "Submit Property for Review"
    )