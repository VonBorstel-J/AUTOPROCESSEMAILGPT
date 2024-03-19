from flask import Flask
from .routes.email_routes import email_bp
from .routes.template_routes import template_bp
# Import other blueprints

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(email_bp)
    app.register_blueprint(template_bp)
    # Register other blueprints
    
    return app
