from flask import Blueprint, jsonify

email_bp = Blueprint('email', __name__, url_prefix='/emails')

@email_bp.route('/', methods=['GET'])
def get_emails():
    # Logic to fetch emails
    return jsonify({"message": "List of emails"})
