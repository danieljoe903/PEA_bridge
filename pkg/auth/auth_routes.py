import os,secrets
import uuid
from flask import render_template, request, session, redirect, url_for, flash,current_app,make_response
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer,BadSignature,SignatureExpired
from flask_mail import Message
from pkg.extension import mail
from pkg.auth import forms
from pkg.auth import auth_bp
from pkg.extension import db
from pkg.model import User


def get_current_user():
    if "user_id" not in session:
        return None
    return db.session.get(User, session['user_id'])

def generate_reset_token(user):

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps({
        "email": user.email,
        "nonce": user.reset_nonce
    }, salt="password-reset-salt")

def verify_reset_token(token, max_age=1800):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    try:
        data = serializer.loads(token, salt="password-reset-salt", max_age=max_age)
    except SignatureExpired:
        return None, "expired"
    except BadSignature:
        return None, "invalid"
    except Exception:
        return None, "invalid"
    
    email= data.get("email")
    nonce = data.get("nonce")

    if not email or not nonce:
        return None,"invaild"
    
    user = User.query.filter_by(email=email).first()

    if not user:
        return None, "invaild"
    
    if user.reset_nonce != nonce:
        return None, "used"
    
    return user
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
            return redirect(url_for("main.homepage"))

        except Exception as e:
            db.session.rollback()
            # print("REGISTER ERROR:", repr(e))   
            flash("Registration failed. Check server log.", "danger")
            return redirect(url_for("auth.register"))

    return render_template("auth/register.html", userform=userform)

@auth_bp.route("/login/", methods=["GET", "POST"])
def login():

    if "admin_id" in session:
        return redirect(url_for("admin.admin_dashboard"))

    if "user_id" in session:
        return redirect(url_for("main.homepage"))

    form = forms.Loginform()

    if form.validate_on_submit():

        user = User.query.filter_by(
            username=form.username.data.strip().lower()
        ).first()

        if not user or not user.check_password(form.password.data):
            flash("Invalid username or password", "danger")
            return redirect(url_for("auth.login"))

        if user.suspended:
            flash("Your account has been suspended. visit homepage to contact us", "danger")
            return redirect(url_for("auth.login"))

        session.clear()
        session["user_id"] = user.user_id
        session["useronline"] = user.username

        flash("Login successful", "success")
        return redirect(url_for("main.homepage"))
    

    return render_template("auth/login.html", form=form)


@auth_bp.route('/logout/')
def logout():
    session.pop('user_id',None)
    session.pop('useronline',None)
    session.clear()
    return redirect(url_for("main.homepage"))

@auth_bp.route("/forgot_password/", methods=['GET','POST'])
def forgot_password():

    if get_current_user():
        return redirect(url_for("main.homepage"))

    form = forms.ForgotPasswordEmailForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if user:
            user.reset_nonce = secrets.token_hex(16)
            db.session.commit()
            send_reset_email(user)

        # do not reveal weather the email exit

        return redirect(url_for("auth.check_box"))
    

    return render_template("auth/forgot_password.html",form=form)


@auth_bp.route("/reset_password/<token>/", methods=["GET","POST"])
def reset_password(token):
    
    if get_current_user():
        return redirect(url_for("main.homepage"))
    
    user, error_type= verify_reset_token(token)

    if not user:
        if error_type == "expired":
            flash("this link has expired: Please rquest for a new one","danger")
        elif error_type == "used":
            flash("this link has been used: Please rquest for a new one","danger")
        else:
             flash("this reset link is invaild","danger")
        return redirect(url_for('auth.forgot_password'))
    
    
    form= forms.ResetPasswordForm()

    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        user.reset_nonce = secrets.token_hex(16)
        db.session.commit()

        flash("Your password have been reset successfully please: login","success")
        return redirect(url_for('auth.login'))
   
    

    return render_template("auth/reset_password.html",form=form)

@auth_bp.route("/resend-reset-link/", methods=["GET", "POST"])
def resend_reset_link():
    
    if get_current_user():
        return redirect(url_for("main.homepage"))

    form = forms.ForgotPasswordEmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()

        if user:

            # invalidate old reset links
            user.reset_nonce = secrets.token_hex(16)
            db.session.commit()

            send_reset_email(user)

        
        return redirect(url_for("auth.check_box"))

    return render_template("auth/resend_reset_link.html", form=form)

@auth_bp.route("/check_inbox/")
def check_box():
    if get_current_user():
        return redirect(url_for("main.homepage"))

    return render_template("auth/check_inbox.html")

def send_reset_email(user):
    token = generate_reset_token(user)
    reset_url = url_for("auth.reset_password", token=token, _external=True)

    msg = Message(
        subject="PEA-Bridge Password Reset",
        recipients=[user.email],
        sender="danieljoe903@gmail.com"
    )

    msg.body = f"""
            Hello {user.user_fname},

            Use the link below to reset your password:

            {reset_url}

            This link will expire in 30 minutes.
            """

    msg.html = f"""
    <div style="margin:0; padding:0; background-color:#f4f6f9; font-family:Arial, Helvetica, sans-serif;">
      <div style="max-width:620px; margin:30px auto; background-color:#ffffff; border-radius:12px; overflow:hidden; border:1px solid #e5e7eb;">
        <div style="background:#0b1320; padding:24px 30px; text-align:center;">
          <h1 style="margin:0; font-size:28px; color:#7acc16; font-weight:700;">PEA-Bridge</h1>
          <p style="margin:8px 0 0; color:#d1d5db; font-size:14px;">Trusted, Reliable and Secure</p>
        </div>

        <div style="padding:32px 30px;">
          <h2 style="margin:0 0 14px; color:#0f172a; font-size:22px;">Password Reset Request</h2>

          <p style="margin:0 0 14px; color:#374151; font-size:15px; line-height:1.7;">
            Hello <strong>{user.user_fname}</strong>,
          </p>

          <p style="margin:0 0 20px; color:#374151; font-size:15px; line-height:1.7;">
            Click the button below to reset your password.
          </p>

          <div style="text-align:center; margin:28px 0;">
            <a href="{reset_url}"
               style="display:inline-block; background-color:#7acc16; color:#08110a; text-decoration:none; padding:14px 28px; border-radius:8px; font-size:15px; font-weight:700;">
              Reset Password
            </a>
          </div>

          <p style="margin:0 0 12px; color:#374151; font-size:14px; line-height:1.7;">
            This link will expire in <strong>30 minutes</strong>.
          </p>

          <p style="margin:0 0 12px; color:#374151; font-size:14px; line-height:1.7;">
            If the button does not work, copy this link:
          </p>

          <p style="margin:0 0 20px; word-break:break-word;">
            <a href="{reset_url}" style="color:#2563eb; text-decoration:none; font-size:14px;">{reset_url}</a>
          </p>
        </div>
      </div>
    </div>
    """

    mail.send(msg)