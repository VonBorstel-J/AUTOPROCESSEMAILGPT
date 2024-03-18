"""Module for interacting with OpenAI's GPT to process emails."""
import logging
import os
import openai
from dotenv import load_dotenv
from retrying import retry

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the OpenAI API key from an environment variable
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Ensure the API key is set
if not OPENAI_API_KEY:
    logging.error("OpenAI API key is not set in environment variables.")
    raise ValueError("OpenAI API key not found.")

openai.api_key = OPENAI_API_KEY

def retry_if_api_error(exception):
    """Return True if we should retry (in this case when it's an APIError), False otherwise"""
    return isinstance(exception, openai.error.OpenAIError)

@retry(stop_max_attempt_number=3, wait_fixed=2000, retry_on_exception=retry_if_api_error)
def process_email_and_generate_response(email_body):
    """
    Processes the given email body using OpenAI's GPT and generates a response.
    
    Parameters:
    email_body (str): The body of the email to process.
    
    Returns:
    tuple: A tuple containing any extracted data and the response text.
    """
    try:
        if email_body is None or email_body.strip() == '':
            logging.warning("Email body is empty or None, skipping processing.")
            return "Error extracting data.", "Sorry, I can't process an empty email."

        logging.info("Sending email content to GPT API for processing.")
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-0125",
            prompt=email_body,
            max_tokens=1500,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )

        # Extracting the text response from the completion object
        response_text = response['choices'][0]['text'].strip()

        return "", response_text  # Return any extracted data along with the response text
    except Exception as e:
        logging.error("An error occurred while interacting with GPT API: %s", e)
        return "Error extracting data.", "Sorry, I can't process your request right now."
