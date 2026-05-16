from datetime import datetime
from flask import current_app
from pkg.extension import db
from pkg.emails import send_property_expired_email
from pkg.model import Property, User
from sqlalchemy import text


def check_expired_properties(app):

    


    with app.app_context():
    
        print("DB:", app.config["SQLALCHEMY_DATABASE_URI"])
        print("PYTHON UTC NOW:", datetime.utcnow())

        db_now = db.session.execute(text("SELECT UTC_TIMESTAMP()")).scalar()
        print("MYSQL UTC NOW:", db_now)

        rows = db.session.execute(text("""
            SELECT property_id, property_status, expires_at
            FROM properties
            WHERE property_status = 'available'
            ORDER BY property_id DESC
            LIMIT 5
        """)).fetchall()

        print("AVAILABLE ROWS:", rows)


        expired_properties = Property.query.filter(
            Property.property_status == "available",
            Property.expires_at.isnot(None),
             Property.expires_at <= datetime.utcnow()
        ).all()

        for listing in expired_properties:

            listing.property_status = "expired"

            user = User.query.get(listing.owner_id)

            if user:
                try:
                    send_property_expired_email(
                    user.email,
                    user.username,
                    listing.property_title
                )
                    
                    print("Email sent to", repr(user.email))


                except Exception as e:
                    print("EMAIL ERROR:",repr(e))
                    print("EMAIL:",repr(user.email))
                    print("SENDER:",repr(current_app.config["MAIL_DEFAULT_SENDER"]))

                
        if expired_properties:
            db.session.commit()

        print(f"{len(expired_properties)} expired properties processed")