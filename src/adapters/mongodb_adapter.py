from contextlib import contextmanager

from pymongo import MongoClient

from ports.db_interface import IDB


class MongoDBAdapter(IDB):
    def __init__(self, uri, db_name, collection_name):
        self._client = MongoClient(uri)
        self._db_name = db_name
        self._collection_name = collection_name

    def save_message(self, body, session=None):
        message_data = body.decode() if isinstance(body, bytes) else body
        data = {"message": message_data}

        db = self._client[self._db_name]
        if session:
            db[self._collection_name].insert_one(data, session=session)
        else:
            db[self._collection_name].insert_one(data)

    @contextmanager
    def transaction(self):
        session = self._client.start_session()
        session.start_transaction()
        try:
            yield session
            session.commit_transaction()
        except Exception as e:
            session.abort_transaction()
            raise e
        finally:
            session.end_session()
