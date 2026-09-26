
from flask import render_template, session, redirect, url_for, flash,request
from werkzeug.security import check_password_hash,generate_password_hash
from sqlalchemy import desc,asc
from datetime import datetime
from functools import wraps
from sqlalchemy.orm import joinedload
from pkg.admin import admin_bp
from pkg.admin.forms import AdminLoginForm,PropertyForm
from pkg.extension import db
from pkg.extension import mail
from flask_mail import Message
from pkg.model import Admin, Property, User,ClientInterest,PropertyAgent,PropertyImage

import os
import uuid
import shutil

from datetime import datetime, timedelta

from flask import (
    current_app,
    render_template,
    redirect,
    url_for,
    flash,
    session,
    request
)

from werkzeug.utils import secure_filename

from pkg.extension import db

from pkg.model import (
    Property,
    PropertyImage,
    State,
    PropertySubmission
)

from pkg.admin import forms
from pkg.emails import (
    send_interest_approved_email,
    send_interest_declined_email,
    send_account_verified_email,
    send_account_reactivated_email,
    send_account_suspended_email,
    send_property_submission_approved_email,
    send_property_submission_rejected_email,
    send_property_archived_email
) 


PROPERTY_ARCHIVE_REASONS = {
    "landlord_withdrew": "Landlord Withdrew Property",
    "sold_elsewhere": "Sold Elsewhere",
    "rented_elsewhere": "Rented Elsewhere",
    "duplicate": "Duplicate Listing",
    "listing_error": "Listing Information Incorrect",
    "admin_removed": "Removed by Administrator",
    "other": "Other"
}


ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def allowed_file(name: str) -> bool:
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_admin():
    admin_id = session.get("admin_id")
    if not admin_id:
        return None
    return db.session.get(Admin, admin_id)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        admin_id = session.get("admin_id")

        if not admin_id:
            flash("Please login as admin.", "warning")
            return redirect(url_for("admin.admin_login"))

        admin = db.session.get(Admin, admin_id)

        if not admin:
            session.clear()
            return redirect(url_for("admin.admin_login"))

        return f(*args, **kwargs)

    return decorated_function

@admin_bp.after_request
def prevent_admin_cache(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@admin_bp.route("/login_admin/", methods=["GET", "POST"])
def admin_login():
    if "user_id" in session:
        return redirect(url_for('main.homepage'))
    
    if "admin_id" in session:
        return redirect(url_for('admin.admin_dashboard'))

    session.pop('_flashes',None)
    form = AdminLoginForm()

    if form.validate_on_submit():
        email = form.admin_email.data.strip().lower()
        password = form.admin_password.data

        admin = Admin.query.filter_by(admin_email=email).first()

        if not admin:
            flash("Invalid admin email or password", "danger")
            return redirect(url_for("admin.admin_login"))
            
        # if admin_password is hashed in DB
        if not check_password_hash(admin.admin_password, password):
            flash("Invalid admin email or password", "danger")
            return redirect(url_for("admin.admin_login"))

        session.clear()
        session["admin_id"] = admin.admin_id
        session["admin_user_id"] = admin.user_id

       
        flash("Welcome admin", "success")
        return redirect(url_for("admin.admin_dashboard"))
    
        
    

    return render_template("admin/admin_login.html", form=form)


@admin_bp.route("/logout/")
def admin_logout():
    session.pop("admin_id", None)
    session.pop("admin_user_id", None)
    flash("Admin logged out successfully", "success")
    return redirect(url_for("admin.admin_login"))


@admin_bp.route("/dashboard/")
@admin_required
def admin_dashboard():
    

    admin = get_current_admin()

    total_users = User.query.count()
    total_properties = Property.query.count()

    pending_properties = (
        Property.query.filter_by(property_status="under_verification").count()
    )
    
    pending_agents=(
        PropertyAgent.query.filter_by(agency_status="pending").count()
    )
    available_properties = (
        Property.query.filter_by(property_status="available").count()
    )

    total_interest = ClientInterest.query.count()
    # print(generate_password_hash('ChChebtmadgtf'))

    return render_template(
        "admin/admin_dashboard.html",
        admin=admin,
        pending_agents=pending_agents,
        total_users=total_users,
        total_properties=total_properties,
        pending_properties=pending_properties,
        available_properties=available_properties,
        total_interest=total_interest,
        active="dashboard"
    )

@admin_bp.route("/properties/")
@admin_required
def verify_properties():

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = 40


    # ==========================================
    # PAGINATED PROPERTY LIST
    # ==========================================

    pagination = (
        Property.query
        .filter(
            Property.property_status
            .not_in(["archived", "expired"]) 
        )
        .order_by(
            desc(Property.created_at)
        )
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )


    properties = pagination.items


    # ==========================================
    # SUMMARY COUNTS
    # These count ALL properties,
    # not just the current page.
    # ==========================================

    total_properties = (
        Property.query
        .filter(
            Property.property_status
            != "archived"
        )
        .count()
    )


    available_count = (
        Property.query
        .filter_by(
            property_status="available"
        )
        .count()
    )


    sold_count = (
        Property.query
        .filter_by(
            property_status="sold"
        )
        .count()
    )


    rented_count = (
        Property.query
        .filter_by(
            property_status="rented"
        )
        .count()
    )


    return render_template(
        "admin/verify_properties.html",
        properties=properties,
        pagination=pagination,
        total_properties=total_properties,
        available_count=available_count,
        sold_count=sold_count,
        rented_count=rented_count,
        active="properties"
    )
@admin_bp.route("/properties/<int:property_id>/approve/", methods=["POST"])
@admin_required
def approve_property(property_id):
    
    prop = Property.query.get_or_404(property_id)
    prop.property_status = "available"
    db.session.commit()

    flash("property approve successfully", "success")
    return redirect(url_for("admin.verify_properties"))

@admin_bp.route("/properties/<int:property_id>/disable/", methods=["POST"])
@admin_required
def disable_property(property_id):
    

    prop = Property.query.get_or_404(property_id)

    # better if your ENUM includes 'rejected'
    prop.property_status = "rejected"
    db.session.commit()

    flash("Property disable successfully.", "warning")
    return redirect(url_for("admin.verify_properties"))

@admin_bp.route("/properties/<int:property_id>/archived/", methods=["POST"])
@admin_required
def archived_property(property_id):

    prop =Property.query.get_or_404(property_id)

    if prop.property_status == "archived":
        flash(
            "This property is already archived.",
            "info"
        )
        return redirect(
            url_for(
                "admin.verify_properties"
            )
        )

    try:
        prop.property_status = "archived"

        db.session.commit()
        flash(
            "Property archived successfully.",
            "success"
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Property archive failed."
        )
        flash(
            "The property could not be archived.",
            "danger"
        )

    return redirect(
        url_for(
            "admin.verify_properties"
        )
    )

@admin_bp.route("/properties/archived/")
@admin_required
def archived_properties():

    page = (
        request.args.get("page",1,type=int)
    )

    per_page = 40

    pagination = (
        Property.query.filter_by(
            property_status="archived"
        ).order_by(
            desc(Property.archived_at),
            desc(Property.created_at)
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    properties= pagination.items

    archived_total = Property.query.filter_by(
        property_status = "archived"
    ).count()


    next_page = request.args.get("next_page")

    return render_template(
        "admin/archived_properties.html",
        archive_total=archived_total,
        pagination=pagination,
        properties=properties,
        active="archived_properties",
        archive_reason=PROPERTY_ARCHIVE_REASONS,
        next_page=next_page,
    )

@admin_bp.route(
    "/properties/<int:property_id>/restore/",
    methods=["POST"]
)
@admin_required
def restore_property(property_id):
    prop = Property.query.get_or_404(property_id)

    if prop.property_status != "archived":
        flash(
            "Only archived properties can be restored.",
            "warning"
        )
        return redirect(
            url_for(
                "admin.archived_properties"
            )
        )

    try:
        prop.property_status = "available"
        prop.archived_at = None
        prop.archive_reason = None
        prop.archive_note = None
        db.session.commit()
        flash(
            "Property restored successfully.",
            "success"
        )

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "Property restoration failed."
        )
        flash(
            "The property could not be restored.",
            "danger"
        )
    return redirect(
        url_for(
            "admin.archived_properties"
        )
    )

@admin_bp.route("/properties/<int:property_id>/reject/", methods=["POST"])
@admin_required
def reject_property(property_id):

    prop = Property.query.get_or_404(property_id)

    # better if your ENUM includes 'rejected'
    prop.property_status = "rejected"
    db.session.commit()

    flash("Property rejected successfully.", "warning")
    return redirect(url_for("admin.verify_properties"))


@admin_bp.route('/properties/<int:property_id>/sold/',methods=['POST'])
@admin_required
def mark_property_sold(property_id):
    
    prop=Property.query.get_or_404(property_id)

    prop.property_status="sold"
    db.session.commit()

    flash("Property marked as sold.", "warning")
    return redirect(url_for("admin.verify_properties"))

@admin_bp.route('/properties/<int:property_id>/rented/',methods=['POST'])
@admin_required
def mark_property_rented(property_id):
    
    prop=Property.query.get_or_404(property_id)

    prop.property_status="rented"
    db.session.commit()

    flash("Property marked as rented.", "warning")
    return redirect(url_for("admin.verify_properties"))


@admin_bp.route("/users/")
@admin_required
def view_users():

    admin = get_current_admin()

    if not admin:
        flash(
            "Only admin can view this page",
            "danger"
        )

        return redirect(
            url_for(
                "admin.admin_login"
            )
        )

    page = request.args.get("page", 1, type=int)

    per_page = 40

    pagination = (
        User.query
        .order_by(desc(User.created_at))
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    users = pagination.items

    return render_template(
        "admin/users.html",
        admin=admin,
        users=users,
        pagination=pagination,
        active="users"
    )


@admin_bp.route("/agents/")
@admin_required
def view_agents():

    admin = get_current_admin()

    agents = (
        PropertyAgent.query
        .order_by(desc(PropertyAgent.agent_id))
        .all()
    )
         
    return render_template(
        "admin/agents.html",
        admin=admin,
        agents=agents,
        active="agents"
    )


@admin_bp.route("/interests/")
@admin_required
def view_interests():
    
    admin=get_current_admin()

    if not admin:
        flash(
          "Only admin is allowed to view this page",
          "danger"  
        )

        return redirect(
            url_for(
                "admin.admin_login"
            )
        )
    
    page = request.args.get("page",1,type=int)

    per_page = 40

    pagination = (
        ClientInterest.query.join(Property).filter(
            Property.property_status !="archived"
        )
        .order_by(desc(ClientInterest.created_at))
        .paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    interests = pagination.items

    return render_template(
        "admin/interests.html",
        admin=admin,
        interests=interests,
        pagination=pagination,
        active="interests"
    )


@admin_bp.route("/users/<int:user_id>/suspend/", methods=["POST"])
@admin_required
def suspend_user(user_id):

    user = User.query.get_or_404(user_id)
    if user.suspended:
        flash(
            "This user is already suspended.",
            "info"
        )
        return redirect(
            url_for("admin.view_users")
        )

    try:
        user.suspended = True
                
        db.session.commit()
        
    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "SUSPENDED USER DATABASE ERROR"
        )

        flash(
            "user could not be suspended. Please try again.",
            "danger"
        )

        return redirect(url_for("admin.view_users"))

    customer_name = (
        user.user_fname or user.users_lname or "customer"
    )

    send_account_suspended_email(
        email=user.email,
        username=customer_name
    )

    flash(
        "Account suspended successfully",
        "warning"
    )
    return redirect(url_for("admin.view_users"))

    

@admin_bp.route("/users/<int:user_id>/activate/", methods=["POST"])
@admin_required
def activate_user(user_id):
   
    user = User.query.get_or_404(user_id)

    if not user.suspended:
        flash(
            "This user is already active.",
            "info"
        )
        return redirect(
            url_for("admin.view_users")
        )

    try:

        user.suspended = False
               
        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "ACCOUNT REACTIVATION DATABASE ERROR"
        )
        flash(
            "Account could not be reactivated. Please try again",
            "danger"
        )
   
        return redirect(url_for("admin.view_users"))

    customer_name = (
        user.user_fname or user.users_lname or "customer"
    )

    send_account_reactivated_email(
        email=user.email,
        username=customer_name
    )

    flash(
       "Account reactivated successfully",
       "success" 
    )

    return redirect(url_for("admin.view_users"))


@admin_bp.route("/users/<int:user_id>/verify/", methods=["POST"])
@admin_required
def verify_user(user_id):

    user = User.query.get_or_404(user_id)

    if user.is_verified:
        flash(
            "This user is already verified.",
            "info"
        )
        return redirect(
            url_for("admin.view_users")
        )

    try:
        user.is_verified = True
        db.session.commit()
        

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "ACCOUNT VERIFICATION DATABASE ERROR"
        )

        flash(
            "Account could not be verify. Please try again",
            "danger"
        )
    
        return redirect(url_for("admin.view_users"))

    customer_name = (
        user.user_fname or user.users_lname or "customer"
    )

    send_account_verified_email(
        email=user.email,
        username=customer_name
    )

    flash("User verified successfully.", "success")
    return redirect(url_for("admin.view_users"))

@admin_bp.route("/users/<int:user_id>/unverify/", methods=["POST"])
@admin_required
def unverify_user(user_id):

    user = User.query.get_or_404(user_id)

    user.is_verified = False
    db.session.commit()

    flash("User verification removed.", "warning")
    return redirect(url_for("admin.view_users"))


@admin_bp.route("/agents/<int:agent_id>/activate/", methods=["POST"])
@admin_required
def activate_agent(agent_id):

    agents = PropertyAgent.query.get_or_404(agent_id)
    agents.agency_status = "active"
    
    db.session.commit()

    flash("Agent activated successfully.", "success")
    return redirect(url_for("admin.view_agents"))


@admin_bp.route("/agents/<int:agent_id>/suspend/", methods=["POST"])
@admin_required
def suspend_agent(agent_id):
    
    agents = PropertyAgent.query.get_or_404(agent_id)
    agents.agency_status = "suspended"
    
    db.session.commit()

    flash("Agent suspended successfully.", "warning")
    return redirect(url_for("admin.view_agents"))


@admin_bp.route("/properties/<int:property_id>/view/")
@admin_required
def view_property(property_id):
    
    prop=Property.query.get_or_404(property_id)

    image=(
        PropertyImage.query.filter_by(property_id=property_id)
        .order_by(asc(PropertyImage.image_id)).all()
    )

    previous_property = (
        Property.query
        .filter(
            Property.property_id < prop.property_id,
            Property.property_status != "archived"
        )
        .order_by(desc(Property.property_id))
        .first()
    )

    # Next record by property ID.
    next_property = (
        Property.query
        .filter(
            Property.property_id > prop.property_id,
            Property.property_status != "archived"
        )
        .order_by(Property.property_id.asc())
        .first()
    )

    
    
    return render_template(
        "admin/property_detail.html",
        prop=prop,
        image=image,
        active="verify_properties",
        archive_reason=PROPERTY_ARCHIVE_REASONS,
        previous_property=previous_property,
        next_property=next_property,
    )


@admin_bp.route(
    "/interests/<int:interest_id>/approve/",
    methods=["POST"]
)
def approve_interest(interest_id):

    if "admin_id" not in session:
        flash("Please sign in as administrator.", "warning")
        return redirect(url_for("admin.admin_login"))


    interest = ClientInterest.query.get_or_404(interest_id)

    prop = interest.property
    user = interest.client

    if not prop:
        flash("Property could not be found.", "danger")
        return redirect(url_for("admin.view_interests"))

    if not user:
        flash("customer could not be found.", "danger")
        return redirect(url_for("admin.view_interests"))

    if interest.interest_status == "approved":
        flash(
            "This interest request has already been approved.",
            "info"
        )
        return redirect(url_for("admin.view_interests"))

    if interest.interest_status == "declined":
        flash(
            "A declined request cannot be approved.",
            "warning"
        )
        return redirect(url_for("admin.view_interests"))

    if prop.property_status == "archived":
        flash(
            "You cannot approve an interest request for an archived property.",
            "warning"
        )
        return redirect(url_for("admin.view_interests"))

    listing_type = (
        str(prop.property_listing)
        .strip()
        .upper()
    )

    if listing_type == "SALE":
        prop.property_status = "sold"

    elif listing_type == "RENT":
        prop.property_status = "rented"

    else:
        raise ValueError(
            "Property has an invalid listing type."
        )

    other_interests = ClientInterest.query.filter(
        ClientInterest.property_id == prop.property_id,
        ClientInterest.interest_id != interest.interest_id,
        ClientInterest.interest_status == "requested"
    )

    try:

        # Approve ONLY this interest request
       

        interest.interest_status = "approved"

         # Mark property as sold
        prop.property_status = "sold"

        # Decline every other pending request
        for other_interest in other_interests:
            other_interest.interest_status = "declined"


        db.session.commit()

        flash(
            "Interest request approved successfully.",
            "success"
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "APPROVED INTEREST REQUEST DATABASE ERROR"
        )

        flash(
            "The interest request could not be approved.",
            "danger"
        )

        return redirect(url_for("admin.view_interests"))

    customer_name = (
        user.user_fname or user.users_lname or "customer"
    )

    email_sent = send_interest_approved_email(
        email=user.email,
        username=customer_name,
        property_title=prop.property_title,
        listing_type=prop.property_listing,
        property_id=prop.property_id

    )

    if not email_sent:
        flash(
            "Property interest was successful, "
            "but the notification email "
            "could not be sent.",
            "warning"
        )

    else:

        flash(
            "Interest request sent was approved.",
            "success"
        )

    # ==========================
    # EMAIL DECLINED CUSTOMERS
    # ==========================

    for other_interest in other_interests:
        other_custutomers = other_interest.client

        if not other_custutomers:
            continue

        other_custutomers_name =(
            other_custutomers.user_fname or other_custutomers.users_lname
            or "customer"
        )

        send_interest_declined_email(
            email=other_custutomers.email,
            username=other_custutomers_name,
            property_title=prop.property_title
        )

    # ==========================
    # SUCCESS
    # ==========================

    flash(
        "Interest approved, property marked as sold, "
        "and other pending requests declined.",
        "success"
    )


    return redirect(
        url_for("admin.view_interests")
    )

@admin_bp.route(
    "/interests/<int:interest_id>/decline/",
    methods=["POST"]
)
def decline_interest(interest_id):

    # Admin authentication
    if "admin_id" not in session:
        flash("Please sign in as administrator.", "warning")
        return redirect(url_for("admin.admin_login"))

    interest = ClientInterest.query.get_or_404(
        interest_id
    )

    prop = interest.property
    user = interest.client

    if not prop:
        flash(
            "Property could not be found.",
            "danger"
        )

        return redirect(
            url_for("admin.view_interests")
        )
    if not user:
        flash(
            "customer could not be found.",
            "danger"
        )
        return redirect(
            url_for("admin.view_interests")
        )

    # -----------------------------------------
    # ALREADY DECLINED
    # -----------------------------------------

    if interest.interest_status == "declined":

        flash(
            "This request has already been declined.",
            "info"
        )

        return redirect(
            url_for("admin.view_interests")
        )


    # -----------------------------------------
    # APPROVED REQUEST
    # -----------------------------------------

    if interest.interest_status == "approved":

        flash(
            "An approved request cannot be declined from here.",
            "warning"
        )

        return redirect(
            url_for("admin.view_interests")
        )


    try:

        interest.interest_status = "declined"

        
        db.session.commit()


        flash(
            "Interest request declined.",
            "success"
        )


    except Exception:

        db.session.rollback()
        current_app.logger.exception(
            "DECLINED INTEREST REQUEST DATABASE ERROR"
        )

        flash(
            "The request could not be declined. Please try again.",
            "danger"
        )


        return redirect(
            url_for("admin.view_interests")
        )

    customer_name =(
        user.user_fname or user.users_lname or "customer"
    )

    send_interest_declined_email(
        email=user.email,
        username=customer_name,
        property_title=prop.property_title
    )

    flash(
        "Interest request was declined.",
        "danger"
    )


    return redirect(
        url_for(
            "property.explore_properties"
        )
    )

@admin_bp.route(
    "/properties/add/",
    methods=["GET", "POST"]
)
def add_property():

    # ==========================================
    # ADMIN AUTHENTICATION
    # ==========================================

    if "admin_id" not in session:

        flash(
            "Please sign in as administrator.",
            "warning"
        )

        return redirect(
            url_for("admin.admin_login")
        )


    form = forms.PropertyForm()


    # ==========================================
    # FORM SUBMISSION
    # ==========================================

    if form.validate_on_submit():

        save_files = []

        try:

            # ==================================
            # STATE
            # ==================================

            state_name = (
                form.state.data
                .strip()
                .title()
            )


            state = State.query.filter_by(
                state_name=state_name
            ).first()


            if not state:

                state = State(
                    state_name=state_name
                )

                db.session.add(state)

                # Flush gives us state_id without
                # committing the transaction yet.
                db.session.flush()


            # ==================================
            # CREATE PROPERTY
            # ==================================

            prop = Property(

                # Admin-managed listing
                owner_id=None,

                agent_id=None,

                property_title=(
                    form.title.data.strip()
                ),

                property_type=(
                    form.type.data
                ),

                description=(
                    form.description.data.strip()
                ),

                adress=(
                    form.address.data.strip()
                ),

                state_id=state.state_id,

                price=form.price.data,

                property_listing="SALE",

                # No verification required.
                property_status="available",

               
            )


            db.session.add(prop)


            # Generate property_id before
            # creating PropertyImage records.
            db.session.flush()


            # ==================================
            # PROPERTY IMAGES
            # ==================================

            images = request.files.getlist(
                "images"
            )


            valid_images =[
                image
                for image in images
                if image
                and image.filename
                and allowed_file(image.filename)
            ]

            if not valid_images:
                flash(
                    "Please upload at least one property image.",
                    "warning"
                )

                return render_template(
                    "admin/add_property.html",
                    form=form
                )
            upload_folder = os.path.join(
                current_app.root_path,
                "static",
                "property_images"
            )


            os.makedirs(
                upload_folder,
                exist_ok=True
            )


            for index, image in enumerate(valid_images):

                if (
                    image
                    and image.filename
                    and allowed_file(image.filename)
                ):

                    safe_filename = secure_filename(
                        image.filename
                    )


                    extension = (
                        safe_filename
                        .rsplit(".", 1)[1]
                        .lower()
                    )


                    unique_name = (
                        f"{uuid.uuid4().hex}."
                        f"{extension}"
                    )


                    save_path = os.path.join(
                        upload_folder,
                        unique_name
                    )


                    image.save(
                        save_path
                    )

                    save_files.append(save_path)


                    property_image = PropertyImage(

                        property_id=prop.property_id,

                        image_url=(
                            "property_images/"
                            f"{unique_name}"
                        ),is_primary=(index == 0)
                    )


                    db.session.add(
                        property_image
                    )


            # ==================================
            # SAVE EVERYTHING
            # ==================================

            db.session.commit()


            flash(
                "Property published successfully.",
                "success"
            )


            return redirect(
                url_for(
                    "admin.view_property",
                    property_id=prop.property_id
                )
            )


        except Exception as error:

            db.session.rollback()

            for file_path in save_files:

                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)

                except OSError:
                    current_app.logger.exception(
                        "Could not remove uploaded property image."
                    )


            current_app.logger.exception(
                "Admin property creation failed."
            )


            flash(
                "The property could not be published. "
                "Please try again.",
                "danger"
            )


    return render_template(
        "admin/add_property.html",
        form=form
    )

@admin_bp.route(
    "/properties/<int:property_id>/edit/",
    methods=["GET", "POST"]
)
def edit_property(property_id):

    if "admin_id" not in session:
        flash(
            "Please sign in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin.admin_login")
        )

    prop = Property.query.get_or_404(property_id)

    form = forms.PropertyForm(obj=prop)


    # ==========================================
    # PRE-FILL FORM
    # ==========================================

    if request.method == "GET":

        form.title.data = prop.property_title
        form.type.data = prop.property_type
        form.address.data = prop.adress
        form.price.data = prop.price
        form.description.data = prop.description

        if prop.state_id:

            state = db.session.get(
                State,
                prop.state_id
            )

            if state:
                form.state.data = state.state_name


    # ==========================================
    # UPDATE PROPERTY
    # ==========================================

    if form.validate_on_submit():

        saved_files = []

        try:

            # ----------------------------------
            # STATE
            # ----------------------------------

            state_name = (
                form.state.data
                .strip()
                .title()
            )

            state = State.query.filter_by(
                state_name=state_name
            ).first()

            if not state:

                state = State(
                    state_name=state_name
                )

                db.session.add(state)

                db.session.flush()


            # ----------------------------------
            # UPDATE DETAILS
            # ----------------------------------

            prop.property_title = (
                form.title.data.strip()
            )

            prop.property_type = (
                form.type.data
            )

            prop.adress = (
                form.address.data.strip()
            )

            prop.state_id = (
                state.state_id
            )

            prop.price = (
                form.price.data
            )

            prop.description = (
                form.description.data.strip()
            )


            # ----------------------------------
            # NEW IMAGES
            # ----------------------------------

            images = request.files.getlist(
                "images"
            )

            valid_images = [
                image
                for image in images
                if (
                    image
                    and image.filename
                    and allowed_file(image.filename)
                )
            ]


            if valid_images:

                upload_folder = os.path.join(
                    current_app.root_path,
                    "static",
                    "property_images"
                )

                os.makedirs(
                    upload_folder,
                    exist_ok=True
                )


                for image in valid_images:

                    safe_filename = secure_filename(
                        image.filename
                    )

                    extension = (
                        safe_filename
                        .rsplit(".", 1)[1]
                        .lower()
                    )

                    unique_name = (
                        f"{uuid.uuid4().hex}."
                        f"{extension}"
                    )

                    save_path = os.path.join(
                        upload_folder,
                        unique_name
                    )

                    image.save(save_path)

                    saved_files.append(
                        save_path
                    )

                    property_image = PropertyImage(
                        property_id=prop.property_id,
                        image_url=(
                            f"property_images/"
                            f"{unique_name}"
                        ),is_primary=False
                    )

                    db.session.add(
                        property_image
                    )


            db.session.commit()

            flash(
                "Property updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "admin.view_property",
                    property_id=prop.property_id
                )
            )


        except Exception:

            db.session.rollback()


            # Delete newly uploaded files if
            # database update failed.

            for file_path in saved_files:

                try:

                    if os.path.exists(file_path):
                        os.remove(file_path)

                except OSError:

                    current_app.logger.exception(
                        "Could not remove uploaded image."
                    )


            current_app.logger.exception(
                "Property update failed."
            )

            flash(
                "The property could not be updated. "
                "Please try again.",
                "danger"
            )


    return render_template(
        "admin/edit_property.html",
        form=form,
        prop=prop
    )



@admin_bp.route(
    "/properties/images/<int:image_id>/delete/",
    methods=["POST"]
)
def delete_property_image(image_id):

    if "admin_id" not in session:
        flash(
            "Please sign in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin.admin_login")
        )

    image = PropertyImage.query.get_or_404(image_id)

    property_id = image.property_id

    # -----------------------------------------
    # PROPERTY MUST KEEP AT LEAST ONE IMAGE
    # -----------------------------------------

    image_count = PropertyImage.query.filter_by(
        property_id=property_id
    ).count()

    if image_count <= 1:

        flash(
            "A property must have at least one image.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.edit_property",
                property_id=property_id
            )
        )
    if image.is_primary:
        flash(
            "You cannot delete the current cover image. "
            "Set another image as the cover first.",
            "warning"
        )
        return redirect(
            url_for(
                "admin.edit_property",
                property_id=property_id
            )
        )

    file_path = os.path.join(
        current_app.root_path,
        "static",
        image.image_url
    )

    backup_path = None


    try:

        # -------------------------------------
        # TEMPORARILY MOVE PHYSICAL FILE
        # -------------------------------------

        if os.path.exists(file_path):

            backup_path = (
                file_path
                + ".deleting"
            )

            os.replace(
                file_path,
                backup_path
            )


        # -------------------------------------
        # DELETE DATABASE RECORD
        # -------------------------------------

        db.session.delete(image)

        db.session.commit()


        # -------------------------------------
        # DATABASE SUCCESSFUL
        # PERMANENTLY DELETE FILE
        # -------------------------------------

        if (
            backup_path
            and os.path.exists(backup_path)
        ):

            try:
                os.remove(backup_path)

            except OSError:
                current_app.logger.exception(
                    "Database image was deleted, "
                    "but temporary image cleanup failed."
                )


        flash(
            "Property image deleted successfully.",
            "success"
        )


    except Exception:

        db.session.rollback()


        # -------------------------------------
        # RESTORE FILE IF DB FAILED
        # -------------------------------------

        if (
            backup_path
            and os.path.exists(backup_path)
        ):

            try:

                os.replace(
                    backup_path,
                    file_path
                )

            except OSError:

                current_app.logger.exception(
                    "Could not restore property image "
                    "after database rollback."
                )


        current_app.logger.exception(
            "Property image deletion failed."
        )


        flash(
            "The property image could not be deleted.",
            "danger"
        )


    return redirect(
        url_for(
            "admin.edit_property",
            property_id=property_id
        )
    )


@admin_bp.route(
    "/properties/images/<int:image_id>/set-primary/",
    methods=["POST"]
)
def set_primary_property_image(image_id):

    if "admin_id" not in session:
        flash(
            "Please sign in as administrator.",
            "warning"
        )
        return redirect(
            url_for("admin.admin_login")
        )

    image = PropertyImage.query.get_or_404(
        image_id
    )

    property_id = image.property_id

    # Already primary
    if image.is_primary:

        flash(
            "This image is already the cover image.",
            "info"
        )

        return redirect(
            url_for(
                "admin.edit_property",
                property_id=property_id
            )
        )

    try:

        # Get every image belonging to this property
        property_images = (
            PropertyImage.query
            .filter_by(
                property_id=property_id
            )
            .all()
        )

        # Remove primary status from all images
        for property_image in property_images:
            property_image.is_primary = False

        # Set selected image as primary
        image.is_primary = True

        db.session.commit()

        flash(
            "Cover image updated successfully.",
            "success"
        )

    except Exception:

        db.session.rollback()

        current_app.logger.exception(
            "Could not update property cover image."
        )

        flash(
            "The cover image could not be updated.",
            "danger"
        )

    # IMPORTANT
    return redirect(
        url_for(
            "admin.edit_property",
            property_id=property_id
        )
    )


@admin_bp.route(
    "/properties/<int:property_id>/relist/",
    methods=["POST"]
)
@admin_required
def relist_property(property_id):

    prop = Property.query.get_or_404(property_id)

    if prop.property_status == "sold":
        flash(
            "Only sold properties can be re-listed.",
            "warning"
        )

        return redirect(
            url_for("admin.verify_properties")
        )

    try:
        approved_interest = ClientInterest.query.filter_by(
            property_id=prop.property_id,
            interest_status = "approved"
        ).first()

        # Change previous approval to declined

        if approved_interest:
            approved_interest.interest_status = "declined"

        prop.property_status = "available"

        db.session.commit()

    except Exception:
        db.session.rollback()

        current_app.logger.exception(
            "PROPERTY RELIST ERROR"
        )

        flash(
            "Property could not be re-listed.",
            "danger"
        )

        return redirect(
            url_for("admin.verify_properties")
        )
    flash(
        "Property re-listed successfully.",
        "success"
    )

    return redirect(
        url_for("admin.verify_properties")
    )


@admin_bp.route("/property-submissions/")
@admin_required
def property_submissions():

    page = request.args.get("page", 1, type=int)

    per_page = 40

    pagination = (
        PropertySubmission.query
        .order_by(
            desc(PropertySubmission.created_at)
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    )

    # Only the properties for the current page
    submissions = pagination.items

    return render_template(
        "admin/property_submissions.html",
        submissions=submissions,
        pagination=pagination,
        active="property_submissions"
    )

@admin_bp.route(
    "/property-submissions/<int:submission_id>/"
)
@admin_required
def view_property_submission(submission_id):

    submission = (
        PropertySubmission.query
        .get_or_404(submission_id)
    )

    return render_template(
        "admin/property_submission_detail.html",
        submission=submission,
        active="property_submissions"
    )

@admin_bp.route(
    "/property-submissions/<int:submission_id>/approve/",
    methods=["POST"]
)
@admin_required
def approve_property_submission(submission_id):

    submission = (
        PropertySubmission.query
        .get_or_404(submission_id)
    )


    # =========================================================
    # 1. PREVENT DUPLICATE REVIEW / PUBLICATION
    # =========================================================

    if (
        submission.submission_status != "pending"
        or submission.published_property_id is not None
    ):

        flash(
            "This property submission has already been "
            "reviewed or published.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )


    # =========================================================
    # 2. VALIDATE LISTING TYPE
    # =========================================================

    if submission.listing_type not in (
        "SALE",
        "RENT"
    ):

        flash(
            "This submission has an invalid listing type.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )


    # =========================================================
    # 3. REQUIRE PROPERTY IMAGES
    # =========================================================

    if not submission.images:

        flash(
            "This submission cannot be published because "
            "no property images were submitted.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )


    # =========================================================
    # 4. FIND THE STATE
    # =========================================================

    submitted_state = submission.state.strip()

    state = (
        State.query
        .filter(
            db.func.lower(State.state_name)
            ==
            submitted_state.lower()
        )
        .first()
    )


    if not state:

        flash(
            f'The state "{submitted_state}" could not be '
            "matched with a state in the system.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )


    # =========================================================
    # 5. MAKE SURE ADMIN SESSION EXISTS
    # =========================================================

    admin_id = session.get("admin_id")

    if not admin_id:

        flash(
            "Your admin session has expired. "
            "Please log in again.",
            "warning"
        )

        return redirect(
            url_for("admin.admin_login")
        )


    # Keep track of physical files copied during approval.
    copied_files = []

    # Keep track of directory created for this property.
    property_folder = None


    try:

        # =====================================================
        # 6. CREATE THE REAL PROPERTY
        # =====================================================

        prop = Property(
            owner_id=None,
            agent_id=None,

            property_title=submission.property_title,
            property_type=submission.property_type,

            description=submission.description,

            # Existing Property model uses "adress"
            adress=submission.address,

            price=submission.price,

            property_status="available",

            property_listing=submission.listing_type,

            state_id=state.state_id,

            # Permanent admin-managed listing
            expires_at=None
        )


        db.session.add(prop)


        # -----------------------------------------------------
        # Generate property_id without committing
        # -----------------------------------------------------

        db.session.flush()


        # =====================================================
        # 7. CREATE PUBLISHED PROPERTY IMAGE FOLDER
        # =====================================================

        property_folder = os.path.join(
            current_app.root_path,
            "static",
            "property_images",
            str(prop.property_id)
        )


        os.makedirs(
            property_folder,
            exist_ok=True
        )


        # =====================================================
        # 8. COPY SUBMISSION IMAGES
        # =====================================================

        for index, submission_image in enumerate(
            submission.images
        ):

            source_path = os.path.join(
                current_app.root_path,
                "static",
                submission_image.image_url
            )

            if not os.path.isfile(source_path):
                raise FileNotFoundError(
                    "Submission image does not exist: "
                    f"{submission_image.image_url}"
                )


            original_filename = os.path.basename(
                submission_image.image_url
            )


            if "." not in original_filename:
                raise ValueError(
                    "A submitted property image has "
                    "an invalid filename."
                )


            extension = (
                original_filename
                .rsplit(".", 1)[1]
                .strip()
                .lower()
            )


            if extension not in {
                "jpg",
                "jpeg",
                "png",
                "webp"
            }:
                raise ValueError(
                    "A submitted property image has "
                    "an unsupported file type."
                )


            unique_filename = (
                f"{uuid.uuid4().hex}.{extension}"
            )


            destination_path = os.path.join(
                property_folder,
                unique_filename
            )


            shutil.copy2(
                source_path,
                destination_path
            )


            copied_files.append(
                destination_path
            )


            image_url = (
                "property_images/"
                f"{prop.property_id}/"
                f"{unique_filename}"
            )


            property_image = PropertyImage(
                property_id=prop.property_id,
                image_url=image_url,
                is_primary=(index == 0)
            )


            db.session.add(
                property_image
            )
        # =====================================================
        # 9. COMPLETE SUBMISSION REVIEW
        # =====================================================

        submission.submission_status = "approved"

        submission.reviewed_at = datetime.utcnow()

        submission.reviewed_by_admin_id = admin_id

        # This is the permanent link between the submission
        # and the public Property.
        submission.published_property_id = prop.property_id

        # Approved submission cannot have a rejection reason.
        submission.rejection_reason = None


        # =====================================================
        # 10. COMMIT EVERYTHING
        # =====================================================

        db.session.commit()


    except Exception:

        db.session.rollback()


        # =====================================================
        # REMOVE PHYSICAL FILES CREATED BEFORE FAILURE
        # =====================================================

        for file_path in copied_files:

            try:

                if os.path.isfile(file_path):
                    os.remove(file_path)

            except OSError:

                current_app.logger.exception(
                    "PROPERTY APPROVAL FILE "
                    "CLEANUP ERROR"
                )


        # Remove empty property directory.
        if property_folder:

            try:

                if (
                    os.path.isdir(property_folder)
                    and not os.listdir(property_folder)
                ):
                    os.rmdir(property_folder)

            except OSError:

                current_app.logger.exception(
                    "PROPERTY APPROVAL DIRECTORY "
                    "CLEANUP ERROR"
                )


        current_app.logger.exception(
            "PROPERTY SUBMISSION APPROVAL ERROR"
        )


        flash(
            "The property could not be published. "
            "No approval changes were saved.",
            "danger"
        )


        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )


    # =========================================================
    # SUCCESS
    # =========================================================

    send_property_submission_approved_email(
        email=submission.landlord_email,
        landlord_name=submission.landlord_name,
        property_title=prop.property_title,
        listing_type=submission.listing_type,
        reference_number=submission.reference_number
    )

    flash(
        f"{submission.reference_number} was approved "
        "and published successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin.view_property_submission",
            submission_id=submission.submission_id
        )
    )

@admin_bp.route(
    "/property-submissions/<int:submission_id>/reject/",
    methods=["POST"]
)
@admin_required
def reject_property_submission(submission_id):

    submission = (
        PropertySubmission.query
        .get_or_404(submission_id)
    )

    # =========================================================
    # 1. ONLY PENDING SUBMISSIONS CAN BE REJECTED
    # =========================================================

    if submission.submission_status != "pending":

        flash(
            "This property submission has already been reviewed.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )


    # =========================================================
    # 2. GET REJECTION REASON
    # =========================================================

    rejection_reason = (
        request.form
        .get("rejection_reason", "")
        .strip()
    )


    # =========================================================
    # 3. VALIDATE REASON
    # =========================================================

    if len(rejection_reason) < 10:

        flash(
            "Please provide a clear reason for rejecting "
            "this property submission.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )


    if len(rejection_reason) > 1000:

        flash(
            "The rejection reason cannot exceed "
            "1000 characters.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )


    # =========================================================
    # 4. GET REVIEWING ADMIN
    # =========================================================

    admin_id = session.get("admin_id")


    if not admin_id:

        flash(
            "Your admin session has expired. "
            "Please log in again.",
            "warning"
        )

        return redirect(
            url_for("admin.admin_login")
        )


    try:

        # =====================================================
        # 5. COMPLETE REVIEW
        # =====================================================

        submission.submission_status = "rejected"

        submission.rejection_reason = rejection_reason

        submission.reviewed_at = datetime.utcnow()

        submission.reviewed_by_admin_id = admin_id

        # Rejected submission has no public Property.
        submission.published_property_id = None


        db.session.commit()


    except Exception:

        db.session.rollback()


        current_app.logger.exception(
            "PROPERTY SUBMISSION REJECTION ERROR"
        )


        flash(
            "The property submission could not be rejected. "
            "Please try again.",
            "danger"
        )


        return redirect(
            url_for(
                "admin.view_property_submission",
                submission_id=submission.submission_id
            )
        )

    send_property_submission_rejected_email(
        email=submission.landlord_email,
        landlord_name=submission.landlord_name,
        property_title=submission.property_title,
        listing_type=submission.listing_type,
        reference_number=submission.reference_number,
        rejection_reason=submission.rejection_reason
    )

    flash(
        f"{submission.reference_number} was rejected successfully.",
        "success"
    )


    return redirect(
        url_for(
            "admin.view_property_submission",
            submission_id=submission.submission_id
        )
    )

@admin_bp.route(
    "/properties/<int:property_id>/archive/",
    methods=["POST"]
)
@admin_required
def archive_property(property_id):

    prop = Property.query.get_or_404(property_id)

    if not prop.property_status == "archived":
        flash(
            "This property is already archived.",
            "warning"
        )
        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )

    archive_reason =(
        request.form.get("archive_reason", "").strip()
    )

    archive_note =(
        request.form.get("archive_note", "").strip()
    )

    if(
        archive_reason not in PROPERTY_ARCHIVE_REASONS
    ):
        flash(
            "Please select a valid archive reason.",
            "warning"
        )
        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )

    if len(archive_note) > 1000:
        flash(
            "The archive note cannot exceed "
            "1000 characters.",
            "warning"
        )
        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )

    listing_type =(
        str(prop.property_listing)
        .strip()
        .upper()
    )

    if(
        archive_reason == "sold_elsewhere"
        and listing_type != "SALE"
    ):
        flash(
            "Only a property listed for sale can "
            "be marked as sold elsewhere.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )
    
    elif(
        archive_reason == "rented_elsewhere"
        and listing_type != "RENT"
    ):
        flash(
            "Only a rental property can be marked "
            "as rented elsewhere.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )
    
    source_submission =(
        prop.source_submission
    )

    try:

        prop.property_status = "archived"
        prop.archive_at = datetime.utcnow()
        prop.archive_reason = archive_reason
        prop.archive_note = archive_note or None

        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "PROPERTY ARCHIVE ERROR"
        )

        flash(
            "The property could not be archived. "
            "Please try again.",
            "danger"
        )
        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )
    
    email_sent = True

    if source_submission:
        email_sent = (
            send_property_archived_email(
                email=source_submission.landlord_email,
                landlord_name=source_submission.landlord_name,
                property_title=prop.property_title,
                listing_type=prop.property_listing,
                reference_number=(
                    source_submission.reference_number
                ),
                archive_reason=archive_reason,
                archive_note=archive_note or None
            )
        )

    elif source_submission and not email_sent:
        flash(
            "Property archived successfully, "
            "but the landlord notification email "
            "could not be sent.",
            "warning"
        )

    else:
        flash(
            "Property archived successfully.",
            "success"
        )


    return redirect(
        url_for(
            "admin.verify_properties"
        )
    )


@admin_bp.route(
    "/properties/<int:property_id>/complete/",
    methods=["POST"]
)
@admin_required
def complete_property(property_id):

    prop = Property.query.get_or_404(property_id)

    if prop.property_status != "available":
        flash(
            "Only an available property can be "
            "marked as sold or rented.",
            "warning"
        )

        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )

    listing_type = (
        str(prop.property_listing)
        .strip()
        .upper()
    )

    # ==========================================
    # SALE PROPERTY
    # ==========================================

    if listing_type == "SALE":
        prop.property_status = "sold"
        success_message =(
            "Property marked as sold successfully."
        )

    elif listing_type == "RENT":
        prop.property_status = "rented"
        success_message = (
            "Property marked as rented successfully."
        )

    else:
        current_app.logger.error(
            "INVALID PROPERTY LISTING TYPE: "
            "%s",
            prop.property_listing
        )
        flash(
            "This property has an invalid "
            "listing type.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )

    try:
        # It is no longer archived.
        prop.archive_at = None
        prop.archive_reason = None
        prop.archive_note = None

        db.session.commit()

    except Exception:
        db.session.rollback()
        current_app.logger.exception(
            "PROPERTY COMPLETION ERROR"
        )

        flash(
            "The property status could not "
            "be updated.",
            "danger"
        )

        return redirect(
            url_for(
                "admin.view_property",
                property_id=prop.property_id
            )
        )


    flash(
        success_message,
        "success"
    )


    return redirect(
        url_for(
            "admin.view_property",
            property_id=prop.property_id
        )
    )
