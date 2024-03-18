import os
from . import app
from dotenv import load_dotenv
load_dotenv() 

# Debugging: Print out the environment variables to check if they're loaded correctly
# print(os.getenv('OPENAI_API_KEY'))
# print(os.getenv('EMAIL_SENDER'))
# print(os.getenv('EMAIL_PASSWORD'))
print(os.getenv('GMAIL_API_CREDENTIALS_JSON'))


if __name__ == '__main__':
    app.run(debug=True)