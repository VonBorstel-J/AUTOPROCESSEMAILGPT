import os
from flask import Flask, jsonify
from gmail_integration import authenticate_gmail_api, get_emails, get_email_content
from email_parser import parse_email, determine_priority
from data_masking import mask_sensitive_data
from gpt_integration import summarize_email, extract_structured_data, generate_response
from mongodb_setup import get_db, init_app
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Initialize MongoDB
init_app(app)

@app.route('/process_emails', methods=['POST'])
def process_emails():
    try:
        gmail_service = authenticate_gmail_api()
        email_ids = get_emails(gmail_service)
        processed_count = 0

        for email_id in email_ids:
            email_content = get_email_content(gmail_service, email_id)
            if email_content:
                parsed_email = parse_email(email_content['raw'])
                if parsed_email:
                    masked_body = mask_sensitive_data(parsed_email['body'])
                    summary = summarize_email(masked_body)
                    if summary:
                        structured_data = extract_structured_data(summary)
                        if structured_data:
                            suggestions = generate_response(structured_data, masked_body)
                            if suggestions:
                                # Process the email with the structured data and suggestions
                                priority = determine_priority(parsed_email)
                                processed_email = {
                                    **parsed_email,
                                    'priority': priority,
                                    'structured_data': structured_data,
                                    'suggestions': suggestions,
                                    'processed': True
                                }

                                # Insert the processed email into MongoDB
                                db = get_db()
                                emails_collection = db.emails
                                emails_collection.insert_one(processed_email)

                                processed_count += 1
                                logging.info(f"Email ID: {email_id} processed and saved.")
                            else:
                                logging.warning(f"Skipping email {email_id} due to failure in generating suggestions.")
                        else:
                            logging.warning(f"Skipping email {email_id} due to failure in extracting structured data.")
                    else:
                        logging.warning(f"Skipping email {email_id} due to failure in summarizing the email.")
                else:
                    logging.warning(f"Skipping email {email_id} due to failure in parsing the email.")
            else:
                logging.warning(f"Skipping email {email_id} due to error in fetching content.")

        return jsonify({"status": "success", "emails_processed": processed_count}), 200
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)