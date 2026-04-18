import os,secrets
from flask import render_template, session, redirect, url_for,request,flash,current_app
from pkg.model import User,Property,ClientInterest,PropertyAgent
from sqlalchemy.orm import joinedload
from sqlalchemy import desc,or_,and_,asc
from pkg.user import user_bp,forms
from pkg.model import db

@user_bp.route("/index/")
def index():
    return render_template("user/index.html")

@user_bp.route("/dashboard/")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = User.query.get(session["user_id"])

    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    total_properties = Property.query.filter(
        Property.owner_id == user.user_id,
        Property.property_status != "archived").count()

    pending_verification = Property.query.filter_by(
        owner_id=user.user_id,
        property_status='under_verification'
    ).count()

    agent_profile = db.session.query(PropertyAgent).filter(PropertyAgent.user_id==user.user_id).first()

    approved_property = Property.query.filter_by(
        owner_id=user.user_id,
        property_status='available'
    ).count()

    total_interest = ClientInterest.query.filter_by(
        client_user_id=user.user_id
    ).count()

    my_properties = Property.query.filter(
        Property.owner_id == user.user_id,
        Property.property_status !="archived"
    ).order_by(desc(Property.created_at)).limit(5).all()

    my_interest =(
        ClientInterest.query.join(Property,ClientInterest.property_id == Property.property_id)
        .filter(ClientInterest.client_user_id == user.user_id,
                Property.property_status != "archived")
                .options(joinedload(ClientInterest.property))
                .order_by(desc(ClientInterest.created_at)).limit(5).all()
    )

    owner_request = ClientInterest.query.join(Property).filter(
        Property.owner_id == user.user_id,
        Property.property_status != "archived"
    ).order_by(desc(Property.created_at)).limit(5).all()
    

    image_url = user.image_url or "uploads/default.png"

    return render_template(
        "user/dashboard.html",
        user=user,
        image_url=image_url,
        active="dashboard",
        total_properties=total_properties,
        total_transactions=0,
        pending_verification=pending_verification,
        approved_property=approved_property,
        total_interest=total_interest,
        my_properties=my_properties,
        my_interest=my_interest,
        agent_profile=agent_profile,
        owner_request=owner_request   )

@user_bp.route("/profile/")
def profile():
    photoform=forms.Photoform()
    resetform=forms.Resetform()
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])
    if not user:
        session.clear()
        return redirect(url_for("auth.login"))

    return render_template("user/profile.html", user=user,photoform=photoform,resetform=resetform,active="profile")




@user_bp.route('/profile_pics/', methods=['POST'])
def profile_pics():
    if "user_id" not in session:
        flash('Please login to continue', 'danger')
        return redirect(url_for('auth.login'))

    photoform = forms.Photoform()

    if not photoform.validate_on_submit():
        flash('Picture not uploaded. Please choose a valid image.', 'danger')
        return redirect(url_for('user.profile'))

    file_obj = photoform.photo.data

    if not file_obj or not file_obj.filename:
        flash('No file selected.', 'danger')
        return redirect(url_for('user.profile'))

    _, extension = os.path.splitext(file_obj.filename)
    newname = secrets.token_hex(10) + extension.lower()

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    save_path = os.path.join(upload_folder, newname)
    file_obj.save(save_path)

    user = db.session.get(User, session['user_id'])
    user.image_url = f"uploads/{newname}"
    db.session.commit()

    flash('Photo updated successfully.', 'success')
    return redirect(url_for('user.profile'))

def get_current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session['user_id'])


@user_bp.route('/update_password/',methods=['GET','POST'])
def update_password():

    user=get_current_user()

    if not user:
        return redirect(url_for('auth.login'))
    
   

    resetform= forms.Resetform()

    if resetform.validate_on_submit():
        
       current_password=resetform.current_password.data
       new_password=resetform.new_password.data

       if not user.check_password(current_password):
           flash('Current password is incorrect','warning')
           return redirect(url_for('user.profile'))
       
       user.set_password(new_password)
       db.session.commit()

       flash('You have successfully updated your password','success')
       return redirect(url_for("user.profile"))
        
    return render_template('user/profile.html',resetform=resetform,user=user)


