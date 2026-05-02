import time

from flask import session, redirect, url_for, flash, g, request
from sqlalchemy.exc import SQLAlchemyError

from pkg.extension import db
from pkg.model import User


TIMEOUT = 300


def setup_inactivity_check(app):

    @app.before_request
    def load_logged_in_user():
        g.user = None
        user_id = session.get("user_id")

        if not user_id:
            return

        try:
            user = db.session.get(User, user_id)
            g.user = user

        except SQLAlchemyError:
            db.session.rollback()
            session.clear()
            flash("Session error. Please login again.", "warning")
            return redirect(url_for("auth.login"))

        if user and user.suspended:
            session.clear()
            flash("Your account has been suspended. Please contact us from the homepage.", "danger")
            return redirect(url_for("auth.login"))

    @app.before_request
    def check_activity():
        allowed_endpoints = {
            "auth.login",
            "auth.register",
            "auth.forgot_password",
            "auth.reset_password",
            "auth.resend_reset_link",
            "auth.check_inbox",
            "main.homepage",
            "main.send_contact_message",
            "static",
        }

        if "user_id" not in session:
            return

        if request.endpoint in allowed_endpoints:
            return

        now = time.time()
        last_act = session.get("last_act")

        if last_act and now - last_act > TIMEOUT:
            session.clear()
            flash("Session expired. Please login again.", "warning")
            return redirect(url_for("auth.login"))

        session["last_act"] = now