from pymongo import MongoClient


class MongoConnection:
    def __init__(self, username, psw):
        # self.host = "cluster0.kah64fo.mongodb.net/?retryWrites=true&w=majority"
        self.host = "chess-analysis.fzfzeem.mongodb.net/?retryWrites=true&w=majority"
        self.username = username
        self.password = psw
        self.client = self.connect()
        self.db = self.client['chess']
        self.collection = self.db['task']

    def connect(self):
        client = MongoClient(f"mongodb+srv://{self.username}:{self.password}@{self.host}")
        print("Connection successful")
        return client
