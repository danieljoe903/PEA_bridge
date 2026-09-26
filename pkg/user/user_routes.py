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


