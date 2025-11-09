from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from app.config import Config
import os

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Login manager settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    # Create upload directories if they don't exist
    upload_base = app.config['UPLOAD_FOLDER']
    for folder in ['cv', 'logos', 'interviews']:
        folder_path = os.path.join(upload_base, folder)
        os.makedirs(folder_path, exist_ok=True)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.super_admin import super_admin_bp
    from app.routes.org_admin import org_admin_bp
    from app.routes.public import public_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(super_admin_bp, url_prefix='/super-admin')
    app.register_blueprint(org_admin_bp, url_prefix='/admin')
    app.register_blueprint(public_bp, url_prefix='')
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Register WebSocket handlers
    from app.sockets import interview_socket
    
    # User loader for Flask-Login
    from app.models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    return app

