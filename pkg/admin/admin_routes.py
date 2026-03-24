
from flask import render_template, session, redirect, url_for, flash
from werkzeug.security import check_password_hash,generate_password_hash
from sqlalchemy import desc,asc
from pkg.admin import admin_bp
from pkg.admin.forms import AdminLoginForm
from pkg.extension import db
from pkg.model import Admin, Property, User,ClientInterest,PropertyAgent,PropertyImage


def get_current_admin():
    admin_id = session.get("admin_id")
    if not admin_id:
        return None
    return db.session.get(Admin, admin_id)


def admin_required():
    return "admin_id" in session


@admin_bp.route("/login_admin/", methods=["GET", "POST"])
def admin_login():
    if "user_id" in session:
        return redirect(url_for('user.dashboard'))
    
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
def admin_dashboard():
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

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
    # print(generate_password_hash('ChChebtmadgtf'))

    return render_template(
        "admin/admin_dashboard.html",
        admin=admin,
        pending_agents=pending_agents,
        total_users=total_users,
        total_properties=total_properties,
        pending_properties=pending_properties,
        available_properties=available_properties,
        active="dashboard"
    )


@admin_bp.route("/properties/")
def verify_properties():
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    admin = get_current_admin()

    properties = (
        Property.query
        .order_by(desc(Property.created_at))
        .all()
    )

    return render_template(
        "admin/verify_properties.html",
        admin=admin,
        properties=properties,
        active="verify_properties"
    )


@admin_bp.route("/properties/<int:property_id>/approve/", methods=["POST"])
def approve_property(property_id):
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    prop = Property.query.get_or_404(property_id)
    prop.property_status = "available"
    db.session.commit()

   
    return redirect(url_for("admin.verify_properties"))

@admin_bp.route("/properties/<int:property_id>/disable/", methods=["POST"])
def disable_property(property_id):
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    prop = Property.query.get_or_404(property_id)

    # better if your ENUM includes 'rejected'
    prop.property_status = "rejected"
    db.session.commit()

    flash("Property disable successfully.", "warning")
    return redirect(url_for("admin.verify_properties"))



@admin_bp.route("/properties/<int:property_id>/reject/", methods=["POST"])
def reject_property(property_id):
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    prop = Property.query.get_or_404(property_id)

    # better if your ENUM includes 'rejected'
    prop.property_status = "rejected"
    db.session.commit()

    flash("Property rejected successfully.", "warning")
    return redirect(url_for("admin.verify_properties"))


@admin_bp.route('/properties/<int:property_id>/sold/',methods=['POST'])
def mark_property_sold(property_id):
    if not admin_required():
        return redirect(url_for("admin.login"))
    prop=Property.query.get_or_404(property_id)

    prop.property_status="sold"
    db.session.commit()

    flash("Property marked as sold.", "warning")
    return redirect(url_for("admin.verify_properties"))


@admin_bp.route("/users/")
def view_users():
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    admin = get_current_admin()

    users = (
        User.query
        .order_by(desc(User.created_at))
        .all()
    )

    return render_template(
        "admin/users.html",
        admin=admin,
        users=users,
        active="users"
    )


@admin_bp.route("/agents/")
def view_agents():
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

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
def view_interests():
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    admin=get_current_admin()

    interests = (
        ClientInterest.query.order_by(desc(ClientInterest.created_at)).all()
    )
    

    return render_template(
        "admin/interests.html",
        admin=admin,
        interests=interests,
        active="interests"
    )


@admin_bp.route("/users/<int:user_id>/suspend/", methods=["POST"])
def suspend_user(user_id):
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    user = User.query.get_or_404(user_id)

    user.suspended = True
    db.session.commit()

    flash("User suspended successfully.", "warning")
    return redirect(url_for("admin.view_users"))


@admin_bp.route("/users/<int:user_id>/activate/", methods=["POST"])
def activate_user(user_id):
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    user = User.query.get_or_404(user_id)

    user.suspended = False
    db.session.commit()

    flash("User activated successfully.", "success")
    return redirect(url_for("admin.view_users"))


@admin_bp.route("/users/<int:user_id>/verify/", methods=["POST"])
def verify_user(user_id):

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    user = User.query.get_or_404(user_id)

    user.is_verified = True
    db.session.commit()

    flash("User verified successfully.", "success")
    return redirect(url_for("admin.view_users"))


@admin_bp.route("/users/<int:user_id>/unverify/", methods=["POST"])
def unverify_user(user_id):

    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    user = User.query.get_or_404(user_id)

    user.is_verified = False
    db.session.commit()

    flash("User verification removed.", "warning")
    return redirect(url_for("admin.view_users"))


@admin_bp.route("/agents/<int:agent_id>/activate/", methods=["POST"])
def activate_agent(agent_id):
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    agents = PropertyAgent.query.get_or_404(agent_id)
    agents.agency_status = "active"
    
    db.session.commit()

    flash("Agent activated successfully.", "success")
    return redirect(url_for("admin.view_agents"))


@admin_bp.route("/agents/<int:agent_id>/suspend/", methods=["POST"])
def suspend_agent(agent_id):
    if not admin_required():
        return redirect(url_for("admin.admin_login"))

    agents = PropertyAgent.query.get_or_404(agent_id)
    agents.agency_status = "suspended"
    
    db.session.commit()

    flash("Agent suspended successfully.", "warning")
    return redirect(url_for("admin.view_agents"))


@admin_bp.route("/properties/<int:property_id>/view/")
def view_property(property_id):
    if not admin_required():
        return redirect(url_for("admin.admin_login"))
    
    prop=Property.query.get_or_404(property_id)

    image=(
        PropertyImage.query.filter_by(property_id=property_id)
        .order_by(asc(PropertyImage.image_id)).all()
    )

    
    
    return render_template("admin/property_detail.html",
                           prop=prop,image=image,active="verify_properties")

