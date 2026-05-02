import os

from flask import Flask, render_template, session
from flask_wtf import CSRFProtect
from sqlalchemy import desc

from pkg.auth import auth_bp
from pkg.user import user_bp
from pkg.admin import admin_bp
from pkg.property import property_bp
from pkg.agent import agent_bp
from pkg.client_interest import interest_bp
from pkg.main import main_bp
from pkg.middleware import setup_inactivity_check
from pkg.model import PropertyAgent, User, ClientInterest, Property


csrf = CSRFProtect()


def create_app():
    from pkg.config import Config
    from pkg.extension import db, migrate, mail

    app = Flask(__name__)

    # Load config first
    app.config.from_object(Config)

    # Safety fallback from .env/os environment
    app.config["SECRET_KEY"] = app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY")
    app.config["ADMIN_EMAIL"] = app.config.get("ADMIN_EMAIL") or os.getenv("ADMIN_EMAIL")
    app.config["PEA_BRIDGE_EMAIL"] = app.config.get("PEA_BRIDGE_EMAIL") or os.getenv("PEA_BRIDGE_EMAIL")

    # Extensions
    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    # Upload folders
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    property_images_folder = os.path.join(app.root_path, "static", "uploads")
    os.makedirs(property_images_folder, exist_ok=True)

    # Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(interest_bp)
    app.register_blueprint(main_bp)

    def get_current_user():
        user_id = session.get("user_id")
        if not user_id:
            return None
        return db.session.get(User, user_id)

    @app.context_processor
    def inject_user_data():
        current_user = get_current_user()
        agent_profile = None
        total_owner_requests = 0

        if current_user:
            agent_profile = PropertyAgent.query.filter_by(
                user_id=current_user.user_id
            ).first()

            total_owner_requests = (
                ClientInterest.query
                .join(Property, ClientInterest.property_id == Property.property_id)
                .filter(
                    Property.owner_id == current_user.user_id,
                    Property.property_status.notin_(["archived", "sold"]),
                    ClientInterest.interest_status != "declined"
                )
                .count()
            )

        return dict(
            current_user=current_user,
            agent_profile=agent_profile,
            total_owner_requests=total_owner_requests
        )

    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("errors/404.html"), 404
    
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception:
            db.session.rollback()
        db.session.remove()
    
    @app.errorhandler(500)
    def internal_server_error(e):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(400)
    def bad_request(e):
        return render_template("errors/400.html"), 400

    setup_inactivity_check(app)

    return app