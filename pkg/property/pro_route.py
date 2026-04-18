import os
import uuid
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, current_app, flash
from werkzeug.utils import secure_filename
from pkg.property import property_bp
from pkg.property import forms
from sqlalchemy import desc,or_,and_,asc
from pkg.extension import db
from pkg.model import Property, PropertyImage,User,PropertyAgent,State,ClientInterest,PropertyDocument

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def allowed_file(name: str) -> bool:
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@property_bp.route("/add/", methods=["GET", "POST"])
def add_property():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    form = forms.PropertyForm()

    agent_profile = PropertyAgent.query.filter_by(
        user_id=session["user_id"]
    ).first()

    if not agent_profile:
        flash("You must apply as an agent before adding a property.", "warning")
        return redirect(url_for("agent.apply"))

    if agent_profile.agency_status == "pending":
        flash("Your agent application is still pending approval.", "warning")
        return redirect(url_for("user.dashboard"))

    if agent_profile.agency_status == "suspended":
        flash("Your agent account has been suspended. You cannot add property.", "danger")
        return redirect(url_for("user.dashboard"))

    if form.validate_on_submit():
        state_name = form.state.data.strip().title()

        state = State.query.filter_by(state_name=state_name).first()
        if not state:
            state = State(state_name=state_name)
            db.session.add(state)
            db.session.commit()

        property = Property(
            owner_id=session["user_id"],
            property_title=form.title.data,
            property_type=form.type.data,
            adress=form.address.data,
            state_id=state.state_id,
            price=form.price.data,
            property_listing="SALE",
            property_status="under_verification",
            agent_id=agent_profile.agent_id if agent_profile else None,
            expires_at=datetime.utcnow() + timedelta(days=14)
        )

        db.session.add(property)
        db.session.commit()

        images = request.files.getlist("images")

        os.makedirs(
            os.path.join(current_app.root_path, "static", "property_images"),
            exist_ok=True
        )

        for image in images:
            if image and image.filename and allowed_file(image.filename):
                ext = secure_filename(image.filename).rsplit(".", 1)[1].lower()
                unique_name = f"{uuid.uuid4().hex}.{ext}"

                save_path = os.path.join(
                    current_app.root_path,
                    "static",
                    "property_images",
                    unique_name
                )
                image.save(save_path)

                property_image = PropertyImage(
                    property_id=property.property_id,
                    image_url=f"property_images/{unique_name}"
                )

                db.session.add(property_image)

        db.session.commit()

        flash("Property added successfully and sent for admin verification.", "success")
        return redirect(url_for("property.list_properties"))

    return render_template(
        "property/add_property.html",
        form=form,
        active="add_property"
    )
# ==================
# # list_properties
# ==================

def get_current_user(): 
    if "user_id" not in session:
        return None
    return db.session.get(User, session["user_id"])

@property_bp.route("/properties/")
def list_properties():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
    
   

    my_properties = (
        Property.query
        .filter(Property.owner_id == user.user_id,
                Property.property_status != "archived")
                .order_by(desc(Property.created_at)).all()
        
    )

    # get a cover image for each property (first image)
    covers = {}
    for p in my_properties:
        cover = (
            PropertyImage.query
            .filter_by(property_id=p.property_id)
            .order_by(asc(PropertyImage.image_id))
            .first()
        )
        covers[p.property_id] = cover.image_url if cover else "property_images/default_property.png"

    return render_template(
        "property/properties.html",
        user=user,
        active="properties",
        my_properties=my_properties,
        covers=covers
    )

@property_bp.route("/property/view/<int:property_id>/")
def view_property(property_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    prop = Property.query.get_or_404(property_id)

    # Only allow owner to view in this dashboard view
    if prop.owner_id != user.user_id:
        flash("You are not allowed to view that property.", "danger")
        return redirect(url_for("property.list_properties"))
    state=State.query.filter_by(state_id=prop.state_id).first()
    
    

    images = (
        PropertyImage.query
        .filter_by(property_id=property_id)
        .order_by(asc(PropertyImage.image_id))
        .all()
    )

    back_page=request.args.get('back_page',"dashboard")

    return render_template(
        "property/property_detail.html",
        user=user,
        active="properties",
        prop=prop,
        images=images,
        state=state,
        back_page=back_page
    )

@property_bp.route("/<int:property_id>/edit/", methods=["GET", "POST"])
def edit_property(property_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    prop = Property.query.get_or_404(property_id)
    if prop.owner_id != user.user_id:
        flash("You are not allowed to edit that property.", "danger")
        return redirect(url_for("property.list_properties"))

    if request.method == "POST":
        state_name=request.form.get('state','')
        state=None
        if state_name:
             state=State.query.filter_by(state_name=state_name).first()

             if not state:
                 state=State(state_name=state_name)
                 db.session.add(state)
                 db.session.commit()
       
        prop.property_title = request.form.get("title", "").strip()
        prop.property_type = request.form.get("type", "").strip()
        prop.adress = request.form.get("address", "").strip()
        prop.price = request.form.get("price") or None
        prop.property_status = request.form.get("status") or prop.property_status

        if state:
            prop.state_id=state.state_id

        db.session.commit()
        flash("Property updated successfully.", "success")
        return redirect(url_for("property.view_property", property_id=property_id))

    return render_template(
        "property/edit_property.html",
        user=user,
        active="properties",
        prop=prop
    )

@property_bp.route("/delete/<int:property_id>/", methods=["POST"])
def delete_property(property_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    prop = Property.query.get_or_404(property_id)

    if prop.owner_id != user.user_id:
        flash("You are not allowed to delete that property.", "danger")
        return redirect(url_for("property.list_properties"))

    prop.property_status = "archived"
    db.session.commit()

    flash("Property removed successfully.", "success")
    return redirect(url_for("property.list_properties"))

from datetime import datetime, timedelta

@property_bp.route("/property/<int:property_id>/")
def public_property_detail(property_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    prop = Property.query.get_or_404(property_id)

    images = (
        PropertyImage.query
        .filter_by(property_id=property_id)
        .order_by(asc(PropertyImage.image_id))
        .all()
    )

    state = State.query.filter_by(state_id=prop.state_id).first()
    

    RE_REQUEST_DAYS = 3
    has_requested = False
    can_request_again = True
    days_left = 0

    existing_requests = (
        ClientInterest.query
        .filter(
            ClientInterest.client_user_id == user.user_id,
            ClientInterest.property_id == prop.property_id
        )
        .order_by(ClientInterest.created_at.desc())
        .all()
    )

    active_request = next(
        (r for r in existing_requests if r.interest_status in ["requested", "approved"]),
        None
    )

    if active_request:
        has_requested = True
        can_request_again = False

    latest_declined = next(
        (r for r in existing_requests if r.interest_status == "declined"),
        None
    )

    if not active_request and latest_declined:
        next_allowed_date = latest_declined.created_at + timedelta(days=RE_REQUEST_DAYS)

        if datetime.utcnow() < next_allowed_date:
            can_request_again = False
            days_left = (next_allowed_date - datetime.utcnow()).days + 1

    next_page = request.args.get("next", "explore")

    return render_template(
        "property/public_property_detail.html",
        user=user,
        prop=prop,
        images=images,
        state=state,
        next_page=next_page,
        has_requested=has_requested,
        can_request_again=can_request_again,
        days_left=days_left
    )


@property_bp.route("/explore/")
def explore_properties():
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))
    

         # expire old available properties
    explore_properties = Property.query.filter(
        Property.property_status == "available",
        Property.expires_at != None,
        Property.expires_at < datetime.utcnow()
    ).all()

    for prop in explore_properties:
        prop.property_status = "expired"

    if explore_properties:
        db.session.commit()

    properties = (
        Property.query
        .filter(Property.property_status == "available")
        .order_by(desc(Property.created_at))
        .all()
    )

    covers = {}
    for p in properties:
        cover = (
            PropertyImage.query
            .filter_by(property_id=p.property_id)
            .order_by(asc(PropertyImage.image_id))
            .first()
        )
        covers[p.property_id] = cover.image_url if cover else "property_images/default_property.png"

    RE_REQUEST_DAYS = 3
    request_status_map = {}

    all_requests = ClientInterest.query.filter_by(client_user_id=user.user_id).all()

    for p in properties:
        property_requests = [r for r in all_requests if r.property_id == p.property_id]

        active_request = next(
            (r for r in sorted(property_requests, key=lambda x: x.created_at, reverse=True)
             if r.interest_status in ["requested", "approved"]),
            None
        )

        latest_declined = next(
            (r for r in sorted(property_requests, key=lambda x: x.created_at, reverse=True)
             if r.interest_status == "declined"),
            None
        )

        request_status_map[p.property_id] = {
            "has_requested": False,
            "can_request_again": True,
            "days_left": 0
        }

        if active_request:
            request_status_map[p.property_id]["has_requested"] = True
            request_status_map[p.property_id]["can_request_again"] = False

        elif latest_declined:
            next_allowed_date = latest_declined.created_at + timedelta(days=RE_REQUEST_DAYS)
            if datetime.utcnow() < next_allowed_date:
                request_status_map[p.property_id]["can_request_again"] = False
                request_status_map[p.property_id]["days_left"] = (
                    next_allowed_date - datetime.utcnow()
                ).days + 1

    return render_template(
        "property/explore_properties.html",
        user=user,
        active="explore",
        properties=properties,
        covers=covers,
        request_status_map=request_status_map
    )

@property_bp.route("/reactivate/<int:property_id>/", methods=["POST"])
def reactivate_property(property_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("auth.login"))

    prop = Property.query.get_or_404(property_id)

    if prop.owner_id != user.user_id:
        flash("You are not allowed to reactivate this property","danger")
        return redirect(url_for("property.list_properties"))
    
    if prop.property_status != "expired":
        flash("only expired properties can be reactivated","warning")
        return redirect(url_for("property.list_properties"))
    
    prop.property_status = "available"
    prop.expires_at = datetime.utcnow() + timedelta(days=14)
    db.session.commit()
    
    flash("property reactivated successfully","success")
    return redirect(url_for("property.list_properties"))


@property_bp.route('/search_view')
def search_view():
    search = request.args.get('search', '').strip()

    if not search:
        return ''

    pro = (
        Property.query
        .outerjoin(State, Property.state_id == State.state_id)
        .filter(
            Property.property_status == "available",
            or_(
                Property.adress.ilike(f'%{search}%'),
                Property.property_title.ilike(f'%{search}%'),
                State.state_name.ilike(f'%{search}%')
            )
        )
        .order_by(Property.created_at.desc())
        .limit(8)
        .all()
    )
   
    result = '<div class="list-group">'

    if pro:
        for p in pro:
            state_name = p.states.state_name if hasattr(p, 'states') and p.states else 'No State'
            result += f'''
            <a href="/property/{p.property_id}/?next=explore"
               class="list-group-item list-group-item-action">
               <strong>{p.property_title or "Property"}</strong><br>
               <small>{p.adress} - {state_name}</small>
            </a>
            '''
    else:
        result += '<div class="list-group-item text-danger">No match found</div>'

    result += '</div>'

    
    return result