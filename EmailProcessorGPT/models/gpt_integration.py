import logging
import os
from data_masking import mask_sensitive_data
import openai
from dotenv import load_dotenv
import json 

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

with open('master_template.json', 'r') as f:
    MASTER_TEMPLATE = json.load(f)

openai.api_key = os.getenv('OPENAI_API_KEY')

## DYNAMIC MASKING IN PRODUCTION ## 

## DYNAMIC MASKING IN PRODUCTION ## 

def summarize_email(email_body):
    """Step 1: Summarize the email to identify key information."""
    try:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-0125", 
            prompt=f"Summarize the following email, focusing on identifying key information relevant to an insurance claim: {email_body}",
            max_tokens=15000,
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
            model="gpt-3.5-turbo-0125",
            prompt=f"{prompt}\n\nInstructions: Use the placeholders and their context to fill in the structured template for an insurance claim. The placeholders follow the format [ENTITY_TYPE:VALUE], where ENTITY_TYPE can be PERSON, EMAIL, PHONE, ADDRESS, etc. Pay special attention to annotations like ':INSURED' or ':CLAIMANT' to understand the role of the entity in the claim. Additionally, look for cues related to the urgency or priority of the claim, the type of claim, and any other relevant details that can help you accurately fill in the template.\n\nMaster Template: {json.dumps(MASTER_TEMPLATE, indent=2)}",
            max_tokens=15000,
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
            model="gpt-3.5-turbo-0125",
            prompt=prompt,
            max_tokens=15000,
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


# Example of chaining these functions for a complete workflow
if __name__ == '__main__':
    email_body = "Your raw email content here"
    summary = summarize_email(email_body)
    if summary:
        structured_data = extract_structured_data(summary)
        if structured_data:
            suggestions = generate_response(structured_data)
            if suggestions:
                logging.info(f"Final Suggestions: {suggestions}")
            else:
                logging.error("Failed to generate suggestions.")
        else:
            logging.error("Failed to extract structured data.")
    else:
        logging.error("Failed to summarize email.")
