from flask import Flask
app = Flask(__name__)

# Configuration loading, if necessary
# app.config.from_pyfile('config.py')

# Database initialization
from database.mongodb_setup import initialize_db
initialize_db(app)

# Import routes
from app.routes import init_routes
init_routes(app)
