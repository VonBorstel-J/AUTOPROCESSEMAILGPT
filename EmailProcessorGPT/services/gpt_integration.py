import logging
import os
from data_masking import mask_sensitive_data
import openai
import json

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load the master template
with open('master_template.json', 'r') as f:
    MASTER_TEMPLATE = json.load(f)

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

def summarize_email(email_body):
    """Step 1: Summarize the email to identify key information."""
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=f"Summarize the following email, focusing on identifying key information relevant to an insurance claim: {email_body}",
            max_tokens=500,
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        summary = response.choices[0].text.strip()
        logging.info(f"Email Summary: {summary}")
        return summary
    except Exception as e:
        logging.error(f"Error summarizing email: {e}")
        return None

def extract_structured_data(prompt):
    """Step 2: Extract structured data based on the prompt."""
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=f"{prompt}\n\nInstructions: Use the placeholders and their context to fill in the structured template for an insurance claim. The placeholders follow the format [ENTITY_TYPE:VALUE], where ENTITY_TYPE can be PERSON, EMAIL, PHONE, ADDRESS, etc. Pay special attention to annotations like ':INSURED' or ':CLAIMANT' to understand the role of the entity in the claim. Additionally, look for cues related to the urgency or priority of the claim, the type of claim, and any other relevant details that can help you accurately fill in the template.\n\nMaster Template: {json.dumps(MASTER_TEMPLATE, indent=2)}",
            max_tokens=1000,
            temperature=0.5,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        structured_data = json.loads(response.choices[0].text.strip())
        logging.info(f"Structured Data: {structured_data}")
        return structured_data
    except Exception as e:
        logging.error(f"Error extracting structured data: {e}")
        return None

def generate_response(structured_data, email_body):
    """Step 3: Generate a draft email or suggestions for next steps."""
    try:
        prompt = f"Based on the following structured information and email body, generate a draft email or suggestions for next steps. Ensure that your response is contextually appropriate and actionable, addressing the underlying narrative or question posed by the email.\n\nStructured Information: {json.dumps(structured_data, indent=2)}\n\nEmail Body: {email_body}"
        response = openai.Completion.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        suggestions = response.choices[0].text.strip()
        logging.info(f"Suggestions/Response: {suggestions}")
        return suggestions
    except Exception as e:
        logging.error(f"Error generating suggestions: {e}")
        return None