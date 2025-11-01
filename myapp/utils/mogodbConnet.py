from pymongo import MongoClient
from django.conf import settings
MOGO_URL = settings.MOGO_URL
MOGO_DB_NAME = settings.MOGO_DB_NAME
class MongoDBConnection:
    def __init__(self):
        try:
            self.client = MongoClient(MOGO_URL)
            self.db = self.client.get_database(MOGO_DB_NAME)
            print("Connected to MongoDB successfully")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def close_connection(self):
        self.client.close()
mongo = MongoDBConnection()