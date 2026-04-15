# backend/db.py
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "neet_learning")

class MongoDB:
    def __init__(self, uri: str = MONGO_URI, db_name: str = DB_NAME):
        self.client = AsyncIOMotorClient(uri)
        self.db = self.client[db_name]

    def users(self):
        return self.db["users"]

    def topics(self):
        return self.db["topics"]

    def questions(self):
        return self.db["questions"]

    def ncert_chunks(self):
        return self.db["ncert_chunks"]

# singleton
mongo = MongoDB()
