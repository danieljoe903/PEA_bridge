from flask import redirect,render_template,request,session,url_for,flash
from sqlalchemy import desc,asc
from pkg.main import forms
from pkg.main import main_bp
from pkg.model import User,Property,PropertyImage,State
from pkg.extension import db
from collections import defaultdict
import random

@main_bp.route("/")
def homepage():

    form= forms.HomeSearchForm()

    properties = (
        Property.query
        .filter_by(property_status="available")
        .order_by(desc(Property.created_at))
        .all()
    )

    # group properties by state
    state_groups = defaultdict(list)
    for prop in properties:
        state_groups[prop.state_id].append(prop)

    # sort states by number of listings (highest first)
    sorted_states = sorted(
        state_groups.items(),
        key=lambda item: len(item[1]),
        reverse=True
    )

    featured_properties = []

    # pick one random property from each top state
    for state_id, props in sorted_states:
        featured_properties.append(random.choice(props))
        if len(featured_properties) == 6:
            break

    # if still fewer than 6, fill with random remaining properties
    if len(featured_properties) < 6:
        remaining = [p for p in properties if p not in featured_properties]
        random.shuffle(remaining)

        for prop in remaining:
            featured_properties.append(prop)
            if len(featured_properties) == 6:
                break

    covers = {}
    for prop in featured_properties:
        cover = (
            PropertyImage.query
            .filter_by(property_id=prop.property_id)
            .order_by(asc(PropertyImage.image_id))
            .first()
        )
        covers[prop.property_id] = (
            cover.image_url if cover else "property_images/default_property.png"
        )

    return render_template(
        "main/homepage.html",
        form=form,
        featured_properties=featured_properties,
        covers=covers
    )

@main_bp.route('/privacy/')
def privacy():
    return render_template('main/privacy.html')


@main_bp.route("/listing/<int:property_id>/")
def home_property_detail(property_id):
    prop = Property.query.get_or_404(property_id)

    images = (
        PropertyImage.query
        .filter_by(property_id=property_id)
        .order_by(asc(PropertyImage.image_id))
        .all()
    )

    return render_template(
        "main/home_property_detail.html",
        prop=prop,
        images=images
    )


@main_bp.route("/search_view/")
def search_view():
    property_type = request.args.get("type", "").strip().lower()
    location = request.args.get("location", "").strip()
    budget = request.args.get("budget", "").strip()

    # if everything is empty, return nothing
    if not property_type and not location and not budget:
        return ""

    # if location is provided, check state first
    state = None
    if location:
        state = State.query.filter(State.state_name.ilike(f"%{location}%")).first()

        if not state:
            return '<div class="alert alert-danger mt-3">State not found.</div>'

    query = Property.query.filter(Property.property_status == "available")

    # if state exists, filter by that exact state
    if state:
        query = query.filter(Property.state_id == state.state_id)

    # optional type filter
    if property_type:
        query = query.filter(Property.property_type == property_type)

    # optional budget filter
    if budget == "under_20m":
        query = query.filter(Property.price < 20000000)
    elif budget == "20m_50m":
        query = query.filter(Property.price >= 20000000, Property.price <= 50000000)
    elif budget == "50m_100m":
        query = query.filter(Property.price >= 50000000, Property.price <= 100000000)
    elif budget == "100m_plus":
        query = query.filter(Property.price > 100000000)

    results = query.order_by(desc(Property.created_at)).all()

    if not results:
        return '<div class="alert alert-warning mt-3">No property found for this search.</div>'

    html = '<div class="row g-3 mt-2">'

    for prop in results:
        cover = (
            PropertyImage.query
            .filter_by(property_id=prop.property_id)
            .order_by(asc(PropertyImage.image_id))
            .first()
        )

        image_url = cover.image_url if cover else "property_images/default_property.png"
        state_name = prop.states.state_name if prop.states else "No State"

        html += f"""
        <div class="col-12 col-md-6 col-lg-4">
          <div class="city">
            <a href="/listing/{prop.property_id}/" class="city-link">
              <img src="/static/{image_url}" alt="{prop.property_title}">
            </a>
            <div class="label">
              <h5 class="fw-bold mb-1">{prop.property_title or "Property"}</h5>
              <div class="small">{state_name} • ₦ {prop.price or 0:,.0f}</div>
            </div>
          </div>
        </div>
        """

    html += "</div>"
    return html