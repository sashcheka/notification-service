from pymongo import MongoClient

from ports.db_interface import IDB


class MongoDBAdapter(IDB):
    def __init__(self, uri, db_name, collection_name):
        self.client = MongoClient(uri)
        self.db_name = db_name
        self.collection_name = collection_name

    def start_session(self):
        return self.client.start_session()

    def save_message(self, data, session=None):
        db = self.client[self.db_name]
        if session:
            db[self.collection_name].insert_one(data, session=session)
        else:
            db[self.collection_name].insert_one(data)
