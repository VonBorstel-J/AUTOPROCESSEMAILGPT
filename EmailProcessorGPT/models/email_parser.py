import logging
import base64
import email
import spacy
import re
from spacy.lang.en import English  
from mongodb_setup import insert_email  

# Load the spaCy language model
nlp = spacy.load("en_core_web_sm")  

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_email(raw_email):
    """Parse the raw email content into a structured format."""
    try:
        email_bytes = base64.urlsafe_b64decode(raw_email.encode('UTF-8'))
        email_message = email.message_from_bytes(email_bytes)
        subject = email_message['Subject']
        sender = email_message['From']
        body = get_body(email_message)
        email_id = email_message['Message-ID']
        parsed_email = {
            'subject': subject,
            'sender': sender,
            'body': body,
            'email_id': email_id
        }
        
        # After parsing, insert the email into MongoDB
        insert_email(parsed_email)
        
        return parsed_email  # You may or may not need to return this based on your workflow
    except Exception as e:
        logging.error(f"Error parsing email: {e}")
        return None

def get_body(email_message):
    """Extract the body from the email message, handling different content types."""
    body = None
    html_body = None
    try:
        for part in email_message.walk():
            content_type = part.get_content_type()
            charset = part.get_content_charset('utf-8')
            if content_type == 'text/plain' and not body:
                payload = part.get_payload(decode=True)
                body = payload.decode(charset, errors='replace')
            elif content_type == 'text/html' and not html_body:
                payload = part.get_payload(decode=True)
                html_body = payload.decode(charset, errors='replace')
        return body if body else html_body
    except Exception as e:
        logging.error(f"Error extracting email body: {e}")
        return None


def determine_priority(parsed_email):
    """Determine the priority of the email based on its content using spaCy."""
    subject = parsed_email['subject']
    body = parsed_email['body']
    doc = nlp(subject + " " + body)

    # Use spaCy's NER to identify entities related to urgency or importance
    urgent_entities = [ent.text.lower() for ent in doc.ents if ent.label_ == 'URGENCY']

    if 'urgent' in urgent_entities or 'emergency' in urgent_entities:
        return 'high'
    elif 'important' in urgent_entities or 'priority' in urgent_entities:
        return 'medium'
    else:
        return 'normal'

def extract_phone_numbers(text):
    """Extract phone numbers from the given text using regular expressions."""
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    phone_numbers = re.findall(phone_pattern, text)
    return phone_numbers

def extract_dates(text):
    """Extract dates from the given text using spaCy."""
    doc = nlp(text)
    dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
    return dates

# Example usage
if __name__ == '__main__':
    raw_email = 'Your base64 encoded email string'
    parsed_email = parse_email(raw_email)
    if parsed_email:
        priority = determine_priority(parsed_email)
        phone_numbers = extract_phone_numbers(parsed_email['body'])
        dates = extract_dates(parsed_email['body'])
        logging.info(f"Email Priority: {priority}")
        logging.info(f"Phone Numbers: {phone_numbers}")
        logging.info(f"Dates: {dates}")