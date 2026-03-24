from flask import redirect, url_for, flash, session, render_template
from sqlalchemy import desc,or_,and_,asc
from pkg.extension import db
from pkg.model import ClientInterest, Property, User
from pkg.client_interest import interest_bp

@interest_bp.route("/request/<int:property_id>/", methods=["POST"])
def request_interest(property_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]

    prop = Property.query.get_or_404(property_id)

    # prevent owner from requesting own property
    if prop.owner_id == user_id:
        flash("You cannot request interest in your own property.", "warning")
        return redirect(url_for("property.explore_properties", property_id=property_id))

    # prevent duplicate request
    exists = ClientInterest.query.filter_by(
        property_id=property_id,
        client_user_id=user_id
    ).first()

    if exists:
        flash("You already requested interest for this property.", "info")
        return redirect(url_for("property.view_property", property_id=property_id))

    interest = ClientInterest(
        property_id=property_id,
        client_user_id=user_id,
        interest_status="requested"
    )
    db.session.add(interest)
    db.session.commit()

    flash("Interest request sent successfully.", "success")
    return redirect(url_for("interest.my_interest"))

@interest_bp.route("/my_interest/")
def my_interest():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    rows = (
        ClientInterest.query
        .filter_by(client_user_id=user.user_id)
        .order_by(desc(ClientInterest.created_at))
        .all()
    )

    # optional: preload properties
    property_map = {}
    for r in rows:
        property_map[r.interest_id] = Property.query.get(r.property_id)

    return render_template(
        "interest/my_interest.html",
        active="interest",
        interests=rows,
        property_map=property_map
    )