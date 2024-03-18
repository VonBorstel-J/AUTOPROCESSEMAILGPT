import re
from typing import List, Tuple

def mask_sensitive_data(text):
    """
    Mask sensitive information in the given text.

    This function identifies patterns or rules to detect sensitive information
    (e.g., names, email addresses, phone numbers, addresses, etc.) and replaces
    them with annotated contextual placeholders.

    Args:
        text (str): The input text to be masked.

    Returns:
        str: The masked text with sensitive information replaced by annotated contextual placeholders.
    """
    # Define regex patterns for sensitive data types
    name_pattern = r'\b[A-Z][a-z]+\s([A-Z][a-z]*\s?)+\b'
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
    address_pattern = r'\b\d+\s+([a-zA-Z]+\s*)+,\s*[A-Za-z]{2,}\s*\d{5}(-\d{4})?\b'

    # Define annotation rules
    annotation_rules = [
        (name_pattern, '[PERSON:INSURED]', '[PERSON:CLAIMANT]'),
        (email_pattern, '[EMAIL:INSURED]', '[EMAIL:CLAIMANT]'),
        (phone_pattern, '[PHONE:INSURED]', '[PHONE:CLAIMANT]'),
        (address_pattern, '[ADDRESS:INSURED]', '[ADDRESS:CLAIMANT]'),
    ]

    # Replace sensitive data with annotated contextual placeholders
    masked_text = text
    for pattern, insured_annotation, claimant_annotation in annotation_rules:
        if 'insured' in text.lower():
            masked_text = re.sub(pattern, insured_annotation, masked_text, flags=re.IGNORECASE)
        else:
            masked_text = re.sub(pattern, claimant_annotation, masked_text, flags=re.IGNORECASE)

    return masked_text

def mask_sensitive_data_from_config(email_content):
    """Masks sensitive information in the email content."""
    # Patterns to identify sensitive information
    patterns = {
        'email': r'[\w\.-]+@[\w\.-]+\.\w+',
        'phone': r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        'name': r'\bMr\.|Ms\.|Mrs\. [A-Za-z]+ [A-Za-z]+\b'  # Simplistic; consider NLP for better accuracy
    }
    
    # Replacement logic
    for key, pattern in patterns.items():
        if key == 'email':
            email_content = re.sub(pattern, '[email]', email_content)
        elif key == 'phone':
            email_content = re.sub(pattern, '[phone]', email_content)
        elif key == 'name':
            email_content = re.sub(pattern, '[name]', email_content)
            
    return email_content