from flask import Flask, jsonify
from gmail_integration import authenticate_gmail_api, get_emails, get_email_content
from gpt_integration import summarize_email, extract_structured_data, generate_response
from mongodb_setup import db, insert_email  # Ensure this setup for MongoDB connection is correct
from data_masking import mask_sensitive_data
import logging
import traceback

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def process_email_content(email_content):
    try:
        masked_body = mask_sensitive_data(email_content['body'])
        summary = summarize_email(masked_body) if masked_body else "Analysis Pending"
        structured_data = extract_structured_data(summary) if summary != "Analysis Pending" else {}
        response = generate_response(structured_data, masked_body) if structured_data else "Response Pending"
        status = "processed" if summary != "Analysis Pending" else "pending_analysis"
        
        return masked_body, summary, structured_data, response, status, None
    except Exception as e:
        logging.error("Error during email processing: %s", e)
        return None, "Analysis Pending", {}, "Response Pending", "error", str(e)

@app.route('/process_emails', methods=['POST'])
def process_emails():
    try:
        gmail_service = authenticate_gmail_api()
        email_ids = get_emails(gmail_service)
        processed_count = 0
        
        for email_id in email_ids:
            if db.emails.count_documents({"email_id": email_id, "processed": True}) == 0:
                email_content = get_email_content(gmail_service, email_id)
                if email_content:
                    masked_body, summary, structured_data, response, status, error_reason = process_email_content(email_content)
                    
                    email_document = {
                        "email_id": email_id,
                        "sender": email_content['sender'],
                        "subject": email_content['subject'],
                        "body": masked_body,
                        "attachments": email_content.get('attachments', []),
                        "processed": status == "processed",
                        "processing_info": {
                            "masked_body": masked_body,
                            "summary": summary,
                            "structured_data": structured_data,
                            "response": response,
                            "status": status,
                            "error_reason": error_reason
                        },
                    }
                    
                    insert_email(email_document)
                    processed_count += 1
                    logging.info(f"Email ID: {email_id} processed and saved. Status: {status}")
                else:
                    logging.warning(f"Skipping email {email_id} due to error in fetching content.")
                    
        return jsonify({"status": "success", "emails_processed": processed_count}), 200
    except Exception as e:
        logging.error("An error occurred: %s", e)
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
