import os,secrets,threading
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
from markupsafe import escape


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
        return None,"invalid"
    
    user = User.query.filter_by(email=email).first()

    if not user:
        return None, "invalid"
    
    if user.reset_nonce != nonce:
        return None, "used"
    
    return user,None

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

            app = current_app._get_current_object()
            thread= threading.Thread(
                target=welcome_email_user,
                args=(app,user.email,user.username)
            )

            thread.start()

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

    reset_url = url_for(
        "auth.reset_password",
        token=token,
        _external=True
    )

    msg = Message(
        subject="Reset Your Flexy Properties Password",
        recipients=[user.email],
        sender=current_app.config["MAIL_DEFAULT_SENDER"]
    )


    # ==========================
    # PLAIN TEXT VERSION
    # ==========================

    msg.body = f"""
                Hello {user.user_fname},

                We received a request to reset the password for your
                Flexy Properties account.

                Use the link below to create a new password:

                {reset_url}

                This password reset link will expire in 30 minutes.

                If you did not request a password reset, you can safely
                ignore this email. Your password will remain unchanged.

                Flexy Properties
                """


                    # ==========================
                    # HTML VERSION
                    # ==========================

    msg.html = f"""
                <!DOCTYPE html>

                <html lang="en">

                <head>

                    <meta charset="UTF-8">

                    <meta
                        name="viewport"
                        content="width=device-width, initial-scale=1.0"
                    >

                    <title>
                        Reset Your Flexy Properties Password
                    </title>

                </head>


                <body style="
                    margin:0;
                    padding:0;
                    background-color:#f4f7f6;
                    font-family:Arial, Helvetica, sans-serif;
                    color:#334155;
                ">

                <table
                    role="presentation"
                    width="100%"
                    cellspacing="0"
                    cellpadding="0"
                    border="0"
                    style="
                        width:100%;
                        background-color:#f4f7f6;
                        padding:40px 15px;
                    "
                >

                    <tr>

        <td align="center">


            <!-- EMAIL CONTAINER -->

            <table
                role="presentation"
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="
                    width:100%;
                    max-width:620px;
                    background:#ffffff;
                    border:1px solid #e2e8f0;
                    border-radius:12px;
                    overflow:hidden;
                "
            >


                <!-- HEADER -->

                <tr>

                    <td
                        align="center"
                        style="
                            background:#0f172a;
                            padding:30px 25px;
                        "
                    >

                        <div style="
                            font-size:27px;
                            font-weight:700;
                            color:#ffffff;
                        ">

                            Flexy

                            <span style="
                                color:#22c55e;
                            ">
                                Properties
                            </span>

                        </div>


                        <p style="
                            margin:8px 0 0;
                            color:#cbd5e1;
                            font-size:13px;
                        ">
                            Account Security
                        </p>

                    </td>

                </tr>


                <!-- CONTENT -->

                <tr>

                    <td style="
                        padding:38px 35px;
                    ">


                        <h1 style="
                            margin:0 0 20px;
                            color:#0f172a;
                            font-size:25px;
                            line-height:1.3;
                        ">
                            Reset Your Password
                        </h1>


                        <p style="
                            margin:0 0 16px;
                            color:#475569;
                            font-size:15px;
                            line-height:1.7;
                        ">

                            Hello

                            <strong>
                                {user.user_fname}
                            </strong>,

                        </p>


                        <p style="
                            margin:0 0 20px;
                            color:#475569;
                            font-size:15px;
                            line-height:1.7;
                        ">
                            We received a request to reset
                            the password for your
                            Flexy Properties account.
                        </p>


                        <p style="
                            margin:0 0 25px;
                            color:#475569;
                            font-size:15px;
                            line-height:1.7;
                        ">
                            Click the button below to create
                            a new password.
                        </p>


                        <!-- RESET BUTTON -->

                        <table
                            role="presentation"
                            cellspacing="0"
                            cellpadding="0"
                            border="0"
                            align="center"
                            style="
                                margin:28px auto;
                            "
                        >

                            <tr>

                                <td
                                    align="center"
                                    bgcolor="#16a34a"
                                    style="
                                        border-radius:7px;
                                    "
                                >

                                    <a
                                        href="{reset_url}"
                                        style="
                                            display:inline-block;
                                            padding:14px 28px;
                                            color:#ffffff;
                                            text-decoration:none;
                                            font-size:15px;
                                            font-weight:700;
                                        "
                                    >
                                        Reset Password
                                    </a>

                                </td>

                            </tr>

                        </table>


                        <!-- EXPIRY NOTICE -->

                        <table
                            role="presentation"
                            width="100%"
                            cellspacing="0"
                            cellpadding="0"
                            border="0"
                            style="
                                width:100%;
                                margin:28px 0;
                                background:#f0fdf4;
                                border:1px solid #bbf7d0;
                                border-radius:8px;
                            "
                        >

                            <tr>

                                <td style="
                                    padding:17px 18px;
                                    color:#166534;
                                    font-size:14px;
                                    line-height:1.6;
                                ">

                                    <strong>
                                        Security notice
                                    </strong>

                                    <br>

                                    This password reset link
                                    will expire in
                                    <strong>
                                        30 minutes.
                                    </strong>

                                </td>

                            </tr>

                        </table>


                        <!-- FALLBACK LINK -->

                        <p style="
                            margin:0 0 8px;
                            color:#64748b;
                            font-size:13px;
                            line-height:1.7;
                        ">
                            If the button doesn't work,
                            copy and paste this link into
                            your browser:
                        </p>


                        <div style="
                            background:#f8fafc;
                            border:1px solid #e2e8f0;
                            border-radius:7px;
                            padding:13px;
                            word-break:break-all;
                        ">

                            <a
                                href="{reset_url}"
                                style="
                                    color:#16a34a;
                                    text-decoration:none;
                                    font-size:12px;
                                    line-height:1.6;
                                "
                            >
                                {reset_url}
                            </a>

                        </div>


                        <!-- DID NOT REQUEST -->

                        <p style="
                            margin:28px 0 0;
                            color:#64748b;
                            font-size:13px;
                            line-height:1.7;
                        ">
                            If you did not request a password
                            reset, you can safely ignore this
                            email. Your password will remain
                            unchanged.
                        </p>

                    </td>

                </tr>


                <!-- FOOTER -->

                <tr>

                    <td
                        align="center"
                        style="
                            background:#f8fafc;
                            border-top:1px solid #e2e8f0;
                            padding:24px 25px;
                        "
                    >

                        <p style="
                            margin:0 0 6px;
                            color:#64748b;
                            font-size:12px;
                            font-weight:600;
                        ">
                            Flexy Properties
                        </p>


                        <p style="
                            margin:0;
                            color:#94a3b8;
                            font-size:11px;
                            line-height:1.6;
                        ">
                            This is an automated account
                            security email. Please do not
                            share your password reset link
                            with anyone.
                        </p>

                    </td>

                </tr>


            </table>

        </td>

    </tr>

</table>

</body>

</html>
"""

    mail.send(msg)



def welcome_email_user(
    app,
    user_email,
    username
):

    with app.app_context():

        try:

            safe_username = escape(username)

            msg = Message(
                subject="Welcome to Flexy Properties",
                recipients=[user_email],
                sender=current_app.config[
                    "MAIL_DEFAULT_SENDER"
                ]
            )


            # ==========================
            # PLAIN TEXT VERSION
            # ==========================

            msg.body = f"""
                Hello {safe_username},

                Welcome to Flexy Properties.

                Your account has been created successfully.

                You can now explore available houses, apartments,
                land and commercial properties and submit an
                interest request when you find a property that
                interests you.

                Thank you for joining Flexy Properties.

                Flexy Properties
                """


            # ==========================
            # HTML VERSION
            # ==========================

            msg.html = f"""
            <!DOCTYPE html>

            <html lang="en">

            <head>

                <meta charset="UTF-8">

                <meta
                    name="viewport"
                    content="width=device-width, initial-scale=1.0"
                >

                <title>
                    Welcome to Flexy Properties
                </title>

            </head>


            <body style="
                margin:0;
                padding:0;
                background-color:#f4f7f6;
                font-family:Arial, Helvetica, sans-serif;
                color:#334155;
            ">

            <table
                role="presentation"
                width="100%"
                cellspacing="0"
                cellpadding="0"
                border="0"
                style="
                    width:100%;
                    background-color:#f4f7f6;
                    padding:40px 15px;
                "
            >

                <tr>

                    <td align="center">


                        <!-- EMAIL CONTAINER -->

                        <table
                            role="presentation"
                            width="100%"
                            cellspacing="0"
                            cellpadding="0"
                            border="0"
                            style="
                                width:100%;
                                max-width:620px;
                                background:#ffffff;
                                border:1px solid #e2e8f0;
                                border-radius:12px;
                                overflow:hidden;
                            "
                        >


                <!-- HEADER -->

                <tr>

                    <td
                        align="center"
                        style="
                            background:#0f172a;
                            padding:30px 25px;
                        "
                    >

                        <div style="
                            font-size:27px;
                            font-weight:700;
                            color:#ffffff;
                        ">

                            Flexy

                            <span style="
                                color:#22c55e;
                            ">
                                Properties
                            </span>

                        </div>


                        <p style="
                            margin:8px 0 0;
                            color:#cbd5e1;
                            font-size:13px;
                        ">
                            Find your next property
                            with confidence
                        </p>

                    </td>

                </tr>


                <!-- CONTENT -->

                <tr>

                    <td style="
                        padding:38px 35px;
                    ">


                        <h1 style="
                            margin:0 0 20px;
                            color:#0f172a;
                            font-size:25px;
                            line-height:1.3;
                        ">
                            Welcome to Flexy Properties
                        </h1>


                        <p style="
                            margin:0 0 16px;
                            color:#475569;
                            font-size:15px;
                            line-height:1.7;
                        ">

                            Hello

                            <strong>
                                {safe_username}
                            </strong>,

                        </p>


                        <p style="
                            margin:0 0 18px;
                            color:#475569;
                            font-size:15px;
                            line-height:1.7;
                        ">
                            Your Flexy Properties account
                            has been created successfully.
                            We're glad to have you with us.
                        </p>


                        <p style="
                            margin:0 0 25px;
                            color:#475569;
                            font-size:15px;
                            line-height:1.7;
                        ">
                            You can now explore available
                            houses, apartments, land and
                            commercial properties and submit
                            an interest request when you find
                            a property that interests you.
                        </p>


                        <!-- ACCOUNT READY BOX -->

                        <table
                            role="presentation"
                            width="100%"
                            cellspacing="0"
                            cellpadding="0"
                            border="0"
                            style="
                                width:100%;
                                margin:25px 0;
                                background:#f0fdf4;
                                border:1px solid #bbf7d0;
                                border-radius:8px;
                            "
                        >

                            <tr>

                                <td style="
                                    padding:18px;
                                    color:#166534;
                                    font-size:14px;
                                    line-height:1.7;
                                ">

                                    <strong>
                                        Your account is ready
                                    </strong>

                                    <br>

                                    Sign in to Flexy Properties
                                    and start exploring available
                                    properties.

                                </td>

                            </tr>

                        </table>


                        <!-- FEATURES -->

                        <table
                            role="presentation"
                            width="100%"
                            cellspacing="0"
                            cellpadding="0"
                            border="0"
                            style="
                                width:100%;
                                margin-top:28px;
                            "
                        >

                            <tr>

                                <td style="
                                    padding:16px 0;
                                    border-bottom:
                                        1px solid #e2e8f0;
                                ">

                                    <strong style="
                                        display:block;
                                        color:#0f172a;
                                        font-size:14px;
                                        margin-bottom:4px;
                                    ">
                                        Explore Properties
                                    </strong>

                                    <span style="
                                        color:#64748b;
                                        font-size:13px;
                                        line-height:1.6;
                                    ">
                                        Browse available houses,
                                        apartments, land and
                                        commercial properties.
                                    </span>

                                </td>

                            </tr>


                            <tr>

                                <td style="
                                    padding:16px 0;
                                    border-bottom:
                                        1px solid #e2e8f0;
                                ">

                                    <strong style="
                                        display:block;
                                        color:#0f172a;
                                        font-size:14px;
                                        margin-bottom:4px;
                                    ">
                                        Request Interest
                                    </strong>

                                    <span style="
                                        color:#64748b;
                                        font-size:13px;
                                        line-height:1.6;
                                    ">
                                        Submit an interest request
                                        for a property you would
                                        like to know more about.
                                    </span>

                                </td>

                            </tr>


                            <tr>

                                <td style="
                                    padding:16px 0;
                                ">

                                    <strong style="
                                        display:block;
                                        color:#0f172a;
                                        font-size:14px;
                                        margin-bottom:4px;
                                    ">
                                        Track Your Interests
                                    </strong>

                                    <span style="
                                        color:#64748b;
                                        font-size:13px;
                                        line-height:1.6;
                                    ">
                                        View the status of your
                                        property interest requests
                                        from your account.
                                    </span>

                                </td>

                            </tr>

                        </table>


                        <p style="
                            margin:30px 0 0;
                            color:#475569;
                            font-size:14px;
                            line-height:1.7;
                        ">
                            Thank you for choosing
                            <strong>
                                Flexy Properties
                            </strong>.
                        </p>

                    </td>

                </tr>


                <!-- FOOTER -->

                <tr>

                    <td
                        align="center"
                        style="
                            background:#f8fafc;
                            border-top:
                                1px solid #e2e8f0;
                            padding:24px 25px;
                        "
                    >

                        <p style="
                            margin:0 0 6px;
                            color:#64748b;
                            font-size:12px;
                            font-weight:600;
                        ">
                            Flexy Properties
                        </p>


                        <p style="
                            margin:0;
                            color:#94a3b8;
                            font-size:11px;
                            line-height:1.6;
                        ">
                            This email was sent because
                            an account was created using
                            this email address.
                        </p>

                    </td>

                </tr>


            </table>

        </td>

    </tr>

</table>

</body>

</html>
"""

            mail.send(msg)

            current_app.logger.info(
                "Welcome email sent successfully."
            )


        except Exception:

            current_app.logger.exception(
                "WELCOME EMAIL ERROR"
            )