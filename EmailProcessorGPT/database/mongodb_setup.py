"""Module for MongoDB database setup and initialization."""
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from flask import EmailProcessorGPT, g

# MongoDB URI - replace <password> with your actual password and adjust the URI as needed
# uri = "mongodb+srv://keystonetester23:keystone1@cluster0.wulp4r5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

uri = os.getenv("MONGO_URI")
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# Define the database name to use
DATABASE_NAME = "emailAutomationDB"
db = client[DATABASE_NAME]


def get_db():
    """Get a MongoDB database connection."""
    if "db" not in g:
        g.db = MongoClient(uri).get_default_database()
    return g.db

def close_db(e=None):
    """Close the MongoDB connection."""
    db = g.pop("db", None)
    if db is not None:
        db.client.close()

def init_app(app):
    """Initialize the app with MongoDB."""
    app.teardown_appcontext(close_db)


# Test connection
def test_connection():
    try:
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(e)

# Example utility function to insert an email document into the 'emails' collection
def insert_email(email_data):
    emails_collection = db.emails  # Accessing the 'emails' collection
    result = emails_collection.insert_one(email_data)  # Inserting the document
    return result.inserted_id  # Returning the ID of the inserted document

# Example usage and connection test
if __name__ == "__main__":
    test_connection()

    # Example insert (remove or comment out after testing)
    test_email = {
        "sender": "test@example.com",
        "subject": "Test Email",
        "body": "This is a test email."
    }
    print("Inserting a test email document...")
    inserted_id = insert_email(test_email)
    print(f"Inserted document ID: {inserted_id}")

    # Fetch and print the inserted document (for testing purposes)
    print("Retrieving the inserted document...")
    inserted_document = db.emails.find_one({"_id": inserted_id})
    print(inserted_document)
