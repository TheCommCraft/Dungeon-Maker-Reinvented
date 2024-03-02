"""
Submodule for basetypes.
"""
from dataclasses import dataclass, field
from pymongo.mongo_client import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection




@dataclass(slots=True)
class BaseMongoDBAtlasSession:
    """
    Base class for MongoDB Atlas sessions.
    """
    URI : str = field(kw_only=True)
    client : MongoClient = field(init=False)
    db : Database = field(init=False)
    users : Collection = field(init=False)
    dungeons : Collection = field(init=False)
    rooms : Collection = field(init=False)





















