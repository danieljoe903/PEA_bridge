from flask import redirect, url_for, flash, session, render_template,sessions
from datetime import datetime,timedelta
from sqlalchemy import desc,or_,and_,asc
from sqlalchemy.orm import joinedload
from pkg.extension import db
from pkg.model import ClientInterest, Property, User,PropertyAgent
from pkg.client_interest import interest_bp

def get_current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])

@interest_bp.route("/request/<int:property_id>/", methods=["POST"])
def request_interest(property_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    prop = Property.query.get_or_404(property_id)

    if prop.property_status != "available":
        flash("This property is no longer available.", "warning")
        return redirect(url_for("property.public_property_detail", property_id=property_id, next="explore"))

    RE_REQUEST_DAYS = 3

    existing_requests = (
        ClientInterest.query
        .filter(
            ClientInterest.client_user_id == user.user_id,
            ClientInterest.property_id == property_id
        )
        .order_by(desc(ClientInterest.created_at))
        .all()
    )

    # block if there is still an active request
    active_request = next(
        (r for r in existing_requests if r.interest_status in ["requested", "approved"]),
        None
    )

    if active_request:
        flash("You already have an active request for this property.", "warning")
        return redirect(url_for("property.public_property_detail", property_id=property_id, next="explore"))

    # check latest declined request cooldown
    latest_declined = next(
        (r for r in existing_requests if r.interest_status == "declined"),
        None
    )

    if latest_declined:
        next_allowed_date = latest_declined.created_at + timedelta(days=RE_REQUEST_DAYS)

        if datetime.utcnow() < next_allowed_date:
            days_left = (next_allowed_date - datetime.utcnow()).days + 1
            flash(f"You can request this property again in {days_left} day(s).", "warning")
            return redirect(url_for("property.public_property_detail", property_id=property_id, next="explore"))

    new_request = ClientInterest(
        client_user_id=user.user_id,
        property_id=property_id,
        interest_status="requested"
    )

    db.session.add(new_request)
    db.session.commit()

    flash("Interest request sent successfully.", "success")
    return redirect(url_for("property.public_property_detail", property_id=property_id, next="explore"))

@interest_bp.route("/my_interest/")
def my_interest():
    if "user_id" not in session:
        return redirect(url_for('auth.login'))
    user= User.query.get(session['user_id'])
    
    my_clientinterest=(
        ClientInterest.query.join(Property)
        .filter(
            ClientInterest.client_user_id == user.user_id,
            Property.property_status != "archived"
        ).options(joinedload(ClientInterest.property)).order_by(desc(ClientInterest.created_at)).all()
    )


    return render_template('interest/my_interest.html',my_clientinterest=my_clientinterest, active="my_interest")


@interest_bp.route("/cancel/<int:interest_id>/",methods=['POST'])
def cancel_request(interest_id):
    user= get_current_user()
    if not user:
        return redirect(url_for('auth.login'))
    
    interest = ClientInterest.query.get_or_404(interest_id)

    if interest.client_user_id != user.user_id:
        flash("You are not allowed to cancel the request","danger")
        return redirect(url_for("interest.my_interest"))
    
    db.session.delete(interest)
    db.session.commit()

    flash("interest request cancelled successfully","success")
    return redirect(url_for("interest.my_interest"))

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

@interest_bp.route('/approved/<int:interest_id>/', methods=['POST'])
def approve_request(interest_id):

    user= get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
    interest= ClientInterest.query.get_or_404(interest_id)

    interest = ClientInterest.query.join(Property).filter(
        ClientInterest.interest_id == interest_id
    ).first_or_404()

    if not interest.property or interest.property.owner_id != user.user_id:
        flash("you are not allowed to approve this request","danger")
        return redirect(url_for("interest.owner_requests"))
    
    if interest.property.property_status == "archived":
        flash("You cannot approve request for archived property ","warning")
        return redirect(url_for("interest.owner_requests"))
    
    if interest.property.property_status == "sold":
        flash("This property has already been sold","warning")
        return redirect(url_for("interest.owner_requests"))

        # approve select request
    interest.interest_status = "approved"

    # mark  property as sold
    interest.property.property_status = "sold"
     
    #  decline every other request on the same 
    others_request =(
        ClientInterest.query.filter(
            ClientInterest.property_id == interest.property_id,
            ClientInterest.interest_id == interest.interest_id
        ).all()
    )
    db.session.commit()

    for req in others_request:
        if req.interest_status == "requested":
            req.interest_status = "declined"

    flash("Request Approved , Property mark as sold","success")
    return redirect(url_for('interest.owner_requests'))

@interest_bp.route('/decline/<int:interest_id>/', methods=['POST'])
def decline_request(interest_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
    
    interest= ClientInterest.query.join(Property).filter(
        ClientInterest.interest_id == interest_id
    ).first_or_404()

    if not interest.property or interest.property.owner_id != user.user_id:
        flash("you are not allowed to decline this request","danger")
        return redirect(url_for("interest.owner_requests"))

    # print("BEFORE:", interest.interest_status )

    interest.interest_status = "declined"
    db.session.commit()
    db.session.refresh(interest)

    # print("AFTER:", interest.interest_status )

    flash("Request Declined", "danger")
    return redirect(url_for('interest.owner_requests'))