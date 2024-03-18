# api/__init__.py
from .chatgpt_api import process_email_and_generate_response
from .gmail_integration import authenticate_gmail_api, get_emails, get_email_content
