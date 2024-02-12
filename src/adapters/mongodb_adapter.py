from pymongo import MongoClient


class MongoDBAdapter:
    def __init__(self, uri):
        self.client = MongoClient(uri)
        self.db = self.client["your_db_name"]
        self.collection = self.db["your_collection_name"]

    def insert_message(self, message):
        self.collection.insert_one(message)
