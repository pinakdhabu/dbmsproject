# db_mongo.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

def create_connection():
    """ create a database connection to a MongoDB database """
    client = None
    try:
        # Note: The user will need to ensure MongoDB is running.
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        # The ismaster command is cheap and does not require auth.
        client.admin.command('ismaster')
        print("Successfully connected to MongoDB!")
    except ConnectionFailure as e:
        print(f"MongoDB Connection Failure: {e}")
        return None

    return client
