"""Module for integrating Gmail API functionality, including authentication, 
email fetching, and content retrieval."""

import os
import base64
import logging

# from google.cloud import storage
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def authenticate_gmail_api():
    """Authenticates to the Gmail API and returns a service object."""
    creds = None
    # Check for token.json to load existing credentials
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If credentials are invalid or not found, log in and save new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=8080)
        with open("token.json", "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def get_emails(gmail_service):
    """Fetches emails and returns a list of message IDs."""
    try:
        response = gmail_service.users().messages().list(userId="me").execute()
        return [msg["id"] for msg in response.get("messages", [])]
    except Exception as e:
        logging.error("Error occurred: %s", e)
        # Handle or re-raise exception as needed
        return []


def get_email_content(gmail_service, email_id):
    """Retrieves the content of an email by its ID."""
    try:
        message = (
            gmail_service.users()
            .messages()
            .get(userId="me", id=email_id, format="full")
            .execute()
        )
        sender, subject, email_body, attachments = "", "", "", []
        # Process headers to extract sender and subject
        for header in message["payload"].get("headers", []):
            if header["name"].lower() == "from":
                sender = header["value"]
            elif header["name"].lower() == "subject":
                subject = header["value"]
        # Process parts to extract body and attachments
        if "parts" in message["payload"]:
            for part in message["payload"]["parts"]:
                body_data = part["body"].get("data")
                if body_data:
                    decoded_data = base64.urlsafe_b64decode(body_data.encode("ASCII"))
                    email_body += decoded_data.decode("utf-8", errors="ignore")
                if part.get("filename"):
                    attachment_id = part["body"].get("attachmentId")
                    attachment = (
                        gmail_service.users()
                        .messages()
                        .attachments()
                        .get(userId="me", messageId=email_id, id=attachment_id)
                        .execute()
                    )
                    attachment_data = base64.urlsafe_b64decode(
                        attachment["data"].encode("ASCII")
                    )
                    attachments.append(
                        {"filename": part["filename"], "data": attachment_data}
                    )
        return {
            "sender": sender,
            "subject": subject,
            "body": email_body,
            "attachments": attachments,
        }
    except Exception as e:
        logging.error("Error fetching email content for ID %s: %s", email_id, e)
        return None


def upload_attachment_to_gcs(filename, data, email_id):
    """
    Mocks the upload of an attachment to Google Cloud Storage and returns a mock URL.
    This is a placeholder function until actual GCS access is established.
    """
    logging.info("Mock uploading %s for email ID %s to GCS.", filename, email_id)
    # Generate a mock URL. In a real scenario, this URL would point to the file in GCS.
    mock_url = f"https://storage.googleapis.com/mock-bucket/{email_id}/{filename}"
    return mock_url
