import os
import re
from dotenv import load_dotenv

load_dotenv()  # Take environment variables from .env.

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
GMAIL_API_CREDENTIALS_JSON = os.getenv("GMAIL_API_CREDENTIALS_JSON")

MONGODB_CONNECTION_STRING = "mongodb+srv://<username>:<password>@<cluster-address>/test?retryWrites=true&w=majority"
DATABASE_NAME = "emailAutomationDB"


def mask_sensitive_data(email_content):
    """Masks sensitive information in the email content."""
    # Patterns to identify sensitive information
    patterns = {
        "email": r"[\w\.-]+@[\w\.-]+\.\w+",
        "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        "name": r"\bMr\.|Ms\.|Mrs\. [A-Za-z]+ [A-Za-z]+\b",  # Simplistic; consider NLP for better accuracy
    }

    # Replacement logic
    for key, pattern in patterns.items():
        if key == "email":
            email_content = re.sub(pattern, "[email]", email_content)
        elif key == "phone":
            email_content = re.sub(pattern, "[phone]", email_content)
        elif key == "name":
            email_content = re.sub(pattern, "[name]", email_content)

    return email_content
