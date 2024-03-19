##Email_processing.py##

import spacy

# Load the spaCy language model
nlp = spacy.load("en_core_web_sm")

def preprocess_email(text):
    """
    Preprocess the email text by analyzing the placeholders and their context.

    Args:
        text (str): The input email text.

    Returns:
        str: The optimized prompt for the GPT model.
    """
    doc = nlp(text)
    placeholders = []

    # Extract placeholders and their context
    for ent in doc.ents:
        if ent.label_ in ['PERSON', 'EMAIL', 'PHONE', 'GPE', 'LOC']:
            context = ' '.join(sent.text for sent in ent.sent.as_doc().sents)
            placeholder = f'[{ent.label_}:{ent.text}]'
            placeholders.append((placeholder, context))

    # Generate the optimized prompt
    prompt = f"Based on the following email text and placeholders, fill in the structured template for an insurance claim:\n\nEmail Text: {text}\n\nPlaceholders:"
    for placeholder, context in placeholders:
        prompt += f"\n{placeholder}: {context}"

    return prompt