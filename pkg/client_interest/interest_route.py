from flask import redirect, url_for, flash,current_app, session, render_template,sessions
from datetime import datetime,timedelta
from sqlalchemy import desc,or_,and_,asc
from sqlalchemy.orm import joinedload
from pkg.extension import db
from pkg.model import ClientInterest, Property, User,PropertyAgent,PropertyImage
from pkg.client_interest import interest_bp
from pkg.emails import send_interest_confirmation,send_new_interest_admin_email

def get_current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])


@interest_bp.route(
    "/request/<int:property_id>/",
    methods=["POST"]
)
def request_interest(property_id):

    user = get_current_user()

    if not user:
        return redirect(
            url_for("auth.login")
        )

    prop = Property.query.get_or_404(
        property_id
    )


    # ==========================
    # PROPERTY AVAILABILITY
    # ==========================

    if prop.property_status != "available":

        flash(
            "This property is no longer available.",
            "warning"
        )

        return redirect(
            url_for(
                "property.public_property_detail",
                property_id=property_id,
                next="explore"
            )
        )


    # ==========================
    # RE-REQUEST COOLDOWN
    # ==========================

    RE_REQUEST_DAYS = 3


    existing_requests = (
        ClientInterest.query
        .filter(
            ClientInterest.client_user_id
            == user.user_id,

            ClientInterest.property_id
            == property_id
        )
        .order_by(
            desc(ClientInterest.created_at)
        )
        .all()
    )


    # ==========================
    # ACTIVE REQUEST CHECK
    # ==========================

    active_request = next(
        (
            request
            for request in existing_requests
            if request.interest_status
            in ["requested", "approved"]
        ),
        None
    )


    if active_request:

        flash(
            "You already have an active request "
            "for this property.",
            "warning"
        )

        return redirect(
            url_for(
                "property.public_property_detail",
                property_id=property_id,
                next="explore"
            )
        )


    # ==========================
    # DECLINED REQUEST COOLDOWN
    # ==========================

    latest_declined = next(
        (
            request
            for request in existing_requests
            if request.interest_status
            == "declined"
        ),
        None
    )


    if latest_declined:

        next_allowed_date = (
            latest_declined.created_at
            + timedelta(
                days=RE_REQUEST_DAYS
            )
        )


        if datetime.utcnow() < next_allowed_date:

            days_left = (
                next_allowed_date
                - datetime.utcnow()
            ).days + 1


            flash(
                f"You can request this property "
                f"again in {days_left} day(s).",
                "warning"
            )

            return redirect(
                url_for(
                    "property.public_property_detail",
                    property_id=property_id,
                    next="explore"
                )
            )


    # ==========================
    # CREATE INTEREST REQUEST
    # ==========================

    try:

        new_request = ClientInterest(
            client_user_id=user.user_id,
            property_id=property_id,
            interest_status="requested"
        )

        db.session.add(new_request)

        db.session.commit()


    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "INTEREST REQUEST DATABASE ERROR"
        )

        flash(
            "Your interest request could not be "
            "submitted. Please try again.",
            "danger"
        )

        return redirect(
            url_for(
                "property.public_property_detail",
                property_id=property_id,
                next="explore"
            )
        )


    # ==========================
    # SEND EMAILS
    # ==========================

    customer_name = (
        user.user_fname
        or user.username
        or "Customer"
    )


    # Customer confirmation email
    send_interest_confirmation(
        email=user.email,
        username=customer_name,
        property_title=prop.property_title
    )


    # Admin notification email
    send_new_interest_admin_email(
        customer_name=customer_name,
        customer_email=user.email,
        property_title=prop.property_title,
        property_id=prop.property_id
    )


    flash(
    "Interest request sent successfully. "
    "We've also sent a confirmation email. "
    "If you don't see it in your inbox, please check "
    "your Spam or Junk folder and mark Flexy Properties "
    "as 'Not spam'.",
    "success"
    )


    return redirect(
        url_for(
            "property.explore_properties"
        )
    )

@interest_bp.route("/my_interest/")
def my_interest():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    # Get this user's property requests/interests
    my_clientinterest = (
        ClientInterest.query
        .join(Property)
        .filter(
            ClientInterest.client_user_id == user.user_id,
            Property.property_status != "archived"
        )
        .options(
            joinedload(ClientInterest.property)
        )
        .order_by(
            desc(ClientInterest.created_at)
        )
        .all()
    )

    # Cover images for properties in THIS user's interests
    covers = {}

    for interest in my_clientinterest:

        p = interest.property

        if not p:
            continue

        image = (
            PropertyImage.query
            .filter_by(property_id=p.property_id,is_primary=True)
            .first()
        )

        if image and image.image_url:
            covers[p.property_id] = image.image_url
        else:
            covers[p.property_id] = "uploads/default-property.jpg"

    return render_template(
        "interest/my_interest.html",
        my_clientinterest=my_clientinterest,
        active="my_interest",
        covers=covers,
    )

@interest_bp.route(
    "/cancel/<int:interest_id>/",
    methods=["POST"]
)
def cancel_request(interest_id):

    user = get_current_user()

    if not user:
        return redirect(url_for("auth.login"))

    interest = ClientInterest.query.get_or_404(
        interest_id
    )

    # Make sure the request belongs to this user
    if interest.client_user_id != user.user_id:
        flash(
            "You are not allowed to cancel this request.",
            "danger"
        )
        return redirect(
            url_for("interest.my_interest")
        )

    # Only pending/requested interests can be cancelled
    if interest.interest_status != "requested":
        flash(
            "This interest request can no longer be cancelled.",
            "warning"
        )
        return redirect(
            url_for("interest.my_interest")
        )

    try:
        db.session.delete(interest)
        db.session.commit()

    except Exception:
        db.session.rollback()

        current_app.logger.exception(
            "CANCEL INTEREST REQUEST ERROR"
        )

        flash(
            "Your interest request could not be cancelled. "
            "Please try again.",
            "danger"
        )

        return redirect(
            url_for("interest.my_interest")
        )

    flash(
        "Interest request cancelled successfully.",
        "success"
    )

    return redirect(
        url_for("interest.my_interest")
    )
@interest_bp.route('/owner/')
def owner_requests():

    user = get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    requests_on_my_properties = ClientInterest.query.join(Property).filter(
        Property.owner_id == user.user_id,
        Property.property_status != "archived"
    ).options(
        joinedload(ClientInterest.client),
        joinedload(ClientInterest.property).joinedload(Property.owner),
        joinedload(ClientInterest.property).joinedload(Property.agent).joinedload(PropertyAgent.user)
        ).order_by(desc(Property.created_at)).all()

    
    return render_template(
        "interest/owner_requests.html",
        active=owner_requests,
        user=user,
       requests_on_my_properties=requests_on_my_properties
    )

