# app/routes.py
from flask import request, jsonify
# Import handlers
from api.gmail_integration import get_email_content
from services.data_masking import mask_sensitive_data

def init_routes(app):
    @app.route('/')
    def index():
        return "Welcome to EmailProcessorGPT!"

    @app.route('/process', methods=['POST'])
    def process_email():
        data = request.json
        masked_data = mask_sensitive_data(data['email_content'])
        return jsonify({"masked_data": masked_data})
