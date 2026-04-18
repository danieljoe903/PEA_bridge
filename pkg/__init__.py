import os
from flask import Flask,render_template,session
from pkg.model import PropertyAgent,User,ClientInterest,Property
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



csrf= CSRFProtect()


def create_app():
    from pkg import config
    from pkg.extension import db,migrate,mail
    
    app=Flask(__name__)

   
    app.config["PEA_BRIDGE_EMAIL"]=os.getenv("PEA_BRIDGE_EMAIL")
    app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
    app.config['ADMIN_EMAIL']=os.getenv('ADMIN_EMAIL')
    app.config.from_object(config.Config)

    db.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app,db)
    mail.init_app(app)

    

    property_images_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(property_images_folder, exist_ok=True)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(agent_bp)
    app.register_blueprint(interest_bp)
    app.register_blueprint(main_bp)

    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    def get_current_user():
        if "user_id" not in session:
            return None
        return db.session.get(User, session['user_id'])
           
    @app.errorhandler(404)
    def mypagenotfound(e):
        return render_template("errors/404.html"),404

            
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template("errors/500.html"),500
    
    @app.errorhandler(400)
    def internal_server_error(e):
        return render_template("errors/400.html"),400
    
    @app.context_processor
    def inject_agent_profile():
        user = get_current_user()

        current_user =None
        agent_profile=None
        total_owner_requests=None


        if "user_id" in session:
            current_user = db.session.get(User, session['user_id'])
            agent_profile=PropertyAgent.query.filter_by(user_id=session['user_id']).first()
            total_owner_requests = ClientInterest.query.join(Property).filter(
                Property.owner_id == user.user_id,
                Property.property_status != "archived",
                Property.property_status != "sold",
                ClientInterest.interest_status != "declined"
            ).order_by(desc(Property.created_at)).count()
        
        return dict(current_user=current_user,agent_profile=agent_profile,total_owner_requests=total_owner_requests)
       

  

    setup_inactivity_check(app)

    # print(app.url_map)

    return app