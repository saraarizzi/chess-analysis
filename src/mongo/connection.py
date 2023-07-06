import os

from pymongo import MongoClient


class MongoConnection:
    def __init__(self):
        self.host = "chess-analysis.fzfzeem.mongodb.net/?retryWrites=true&w=majority"
        self.username = os.getenv("MONGO_USER")
        self.password = os.getenv("MONGO_PSW")
        self.client = self.connect()
        self.db = self.client['chess']
        self.collection = self.db['task']

    def connect(self):
        client = MongoClient(f"mongodb+srv://{self.username}:{self.password}@{self.host}")
        print("Connection successful")
        return client
