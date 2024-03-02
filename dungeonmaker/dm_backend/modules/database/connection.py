"""
Submodule for database connections.
"""
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from .basetypes import BaseMongoDBAtlasSession






class MongoDBAtlasSession(BaseMongoDBAtlasSession):
    """
    Class for MongoDB Atlas sessions.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = MongoClient(self.URI, server_api=ServerApi('1'))
        try:
            self.client.admin.command('ping')
        except Exception as e:
            raise ConnectionError("The connection didn't work.") from e
        self.db = self.client["dungeon_maker_reinvented_db"]
        self.users = self.db["users"]
        self.rooms = self.db["rooms"]
        self.dungeons = self.db["dungeons"]
















