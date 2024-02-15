from pymongo import MongoClient

from ports.db_interface import IDB


class MongoDBAdapter(IDB):
    def __init__(self, uri, db_name, collection_name):
        self.client = None
        self.uri = uri
        self.db_name = db_name
        self.collection_name = collection_name

    def save_message(self, data):
        if self.client is None:
            self.client = MongoClient(self.uri)
        db = self.client[self.db_name]
        db[self.collection_name].insert_one(data)
