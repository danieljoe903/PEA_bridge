import time
from flask import session, redirect, url_for, flash, g, request
from pkg.extension import db
from pkg.model import User

TIMEOUT = 300

def setup_inactivity_check(app):
    @app.before_request
    def load_logged_in_user():
        g.user = None
        user_id = session.get("user_id")
        if user_id:
            g.user = db.session.get(User, user_id)
        if "user_id" in session:
            user =db.session.get(User, session['user_id'])

            if user and user.suspended:
                session.clear()
                flash("Your account has been suspended contact us at homepage", "danger")
                return redirect(url_for("auth.login"))

    @app.before_request
    def check_activity():
        allowed = {"auth.login", "auth.register", "static"}

        if "user_id" not in session:
            return

        if request.endpoint in allowed:
            return

        now = time.time()
        last_act = session.get("last_act")

        if last_act and now - last_act > TIMEOUT:
            session.clear()
            flash("Session expired. Please login again.", "warning")
            return redirect(url_for("auth.login"))

        session["last_act"] = now

    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response