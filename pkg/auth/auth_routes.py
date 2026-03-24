import os
import uuid
from flask import render_template, request, session, redirect, url_for, flash,current_app,make_response
from werkzeug.utils import secure_filename
from pkg.auth import forms
from pkg.auth import auth_bp
from pkg.extension import db
from pkg.model import User

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

def allowed_file(name: str) -> bool:
    return "." in name and name.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@auth_bp.route("/register/", methods=["GET", "POST"])
def register():
    userform = forms.Register()

   
    if userform.validate_on_submit():
        try:
            username = userform.username.data.strip().lower()
            email = userform.email.data.strip().lower()

            if User.query.filter_by(username=username).first():
                flash("Username already exists", "danger")
                return redirect(url_for("auth.register"))

            if User.query.filter_by(email=email).first():
                flash("Email already exists", "danger")
                return redirect(url_for("auth.register"))

            image_url = "uploads/default.png"

            # ✅ ensure uploads folder exists
            os.makedirs(current_app.config["UPLOAD_FOLDER"], exist_ok=True)

            if userform.image.data and userform.image.data.filename:
                file = userform.image.data
                if not allowed_file(file.filename):
                    flash("Images only: jpg, jpeg, png, webp", "danger")
                    return redirect(url_for("auth.register"))

                ext = secure_filename(file.filename).rsplit(".", 1)[1].lower()
                unique_name = f"{uuid.uuid4().hex}.{ext}"
                upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_name)
                file.save(upload_path)
                image_url = f"uploads/{unique_name}"

            user = User(
                user_fname=userform.firstname.data.strip(),
                users_lname=userform.lastname.data.strip(),
                email=email,
                phone=userform.phone.data.strip(),
                image_url=image_url,
                username=username,
            )
            user.set_password(userform.user_password.data)  # ✅ hashed

            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.user_id
            return redirect(url_for("user.dashboard"))

        except Exception as e:
            db.session.rollback()
            # print("REGISTER ERROR:", repr(e))   
            flash("Registration failed. Check server log.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html", userform=userform)


@auth_bp.route("/login/", methods=["GET", "POST"])
def login():

    if "admin_id" in session:
        return redirect(url_for('admin.admin_dashboard'))
    
    if "user_id" in session:
        return redirect(url_for('user.dashboard'))
    session.pop('_flashes',None)
    form = forms.Loginform()

    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.username.data.strip().lower()
        ).first()

        if not user or not user.check_password(form.password.data):
            flash("Invalid username or password", category="danger")
            return redirect(url_for("auth.login"))
        
        session["user_id"] = user.user_id
        session['useronline']=user.username

        return redirect(url_for("user.dashboard"))

    return render_template("auth/login.html", form=form)


@auth_bp.route('/logout/')
def logout():
    session.pop('user_id',None)
    session.pop('useronline',None)
    session.clear()
    return redirect(url_for("auth.login"))