import os
from flask import Flask,render_template
from flask_wtf import CSRFProtect
from pkg.auth import auth_bp
from pkg.user import user_bp
from pkg.admin import admin_bp
from pkg.property import property_bp
from pkg.agent import agent_bp
from pkg.client_interest import interest_bp 
from pkg.main import main_bp
from pkg.middleware import setup_inactivity_check


csrf= CSRFProtect()

def create_app():
    from pkg.config import Config
    from pkg.extension import db,migrate
    
    app=Flask(__name__)

    app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
    app.config['ADMIN_EMAIL']=os.getenv('ADMIN_EMAIL')
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app,db)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(interest_bp)
    app.register_blueprint(main_bp)

 
           
    @app.errorhandler(404)
    def mypagenotfound(e):
        return render_template("errors/404.html"),404

            
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/404.html"),500

    setup_inactivity_check(app)

    # print(app.url_map)

    return app