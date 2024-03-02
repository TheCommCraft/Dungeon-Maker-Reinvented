"""
Submodule for Database Abstractions.
"""
from typing import Literal
from dataclasses import dataclass, field
from .basetypes import BaseMongoDBAtlasSession
from ..dm.dba import BaseDatabaseAbstraction
from ..dm.dmtypes import UserId, DungeonId, RoomId

@dataclass(slots=True)
class MongoDBDatabaseAbstraction(BaseDatabaseAbstraction):
    """
    Class for MongoDB database abstractions.
    """
    connection : BaseMongoDBAtlasSession = field(kw_only=True)
    
    def select_user(self, user_id : UserId = None, *, fields : dict = None) -> dict:
        """
        Abstraction to select a user.
        """
        fields = fields or {}
        if user_id is not None:
            fields["user_id"] = user_id
        return dict(self.connection.users.find_one(fields))
    
    def select_dungeon(self, dungeon_id : DungeonId = None, *, fields : dict = None) -> dict:
        """
        Abstraction to select a dungeon.
        """
        fields = fields or {}
        if dungeon_id is not None:
            fields["dungeon_id"] = dungeon_id
        return dict(self.connection.dungeons.find_one(fields))
    
    def select_room(self, room_id : RoomId = None, *, fields : dict = None) -> dict:
        """
        Abstraction to select a room.
        """
        fields = fields or {}
        if room_id is not None:
            fields["room_id"] = room_id
        return dict(self.connection.rooms.find_one(fields))
    
    def update_user(self, user_id : UserId = None, *, fields : dict = None, updator : dict = None):
        """
        Abstraction to update a user.
        """
        fields = fields or {}
        if user_id is not None:
            fields["user_id"] = user_id
        return self.connection.users.update_one(fields, updator)
    
    def update_dungeon(self, dungeon_id : DungeonId = None, *, fields : dict = None, updator : dict = None):
        """
        Abstraction to update a dungeon.
        """
        fields = fields or {}
        if dungeon_id is not None:
            fields["dungeon_id"] = dungeon_id
        return self.connection.dungeons.update_one(fields, updator)
    
    def update_room(self, room_id : RoomId = None, *, fields : dict = None, updator : dict = None):
        """
        Abstraction to update a room.
        """
        fields = fields or {}
        if room_id is not None:
            fields["room_id"] = room_id
        return self.connection.rooms.update_one(fields, updator)
    
    def insert_user(self, *, data : dict = None):
        """
        Abstraction to insert a user.
        """
        return self.connection.users.insert_one(data)

    def insert_dungeon(self, *, data : dict = None):
        """
        Abstraction to insert a dungeon.
        """
        return self.connection.dungeons.insert_one(data)
    
    def insert_room(self, *, data : dict = None):
        """
        Abstraction to insert a room.
        """
        return self.connection.rooms.insert_one(data)
    
    def random_dungeons(self, *, amount : int = 1) -> list[dict]:
        """
        Abstraction to select random dungeons.
        """
        aggregator = [
            {
                "$sample":
                {
                    "size": amount,
                },
            },
            {
                "$addFields":
                {
                    "score": {
                    "$add": [
                        {
                        "$multiply": [
                            20,
                            {
                            "$size": "$likers",
                            },
                        ],
                        },
                        "$views",
                    ],
                    },
                },
            },
        ]
        return list(self.connection.dungeons.aggregate(aggregator))
    
    def sorted_dungeons(
        self, 
        *, 
        amount : int = 20, 
        offset : int = 0, 
        field : str = "score", 
        aggregation : list[dict] = [{"$addFields":{"score": {"$add": [{"$multiply": [20,{"$size": "$likers"},]},"$views"]}}}]
    ) -> list[dict]:
        """
        Abstraction to select random dungeons.
        """
        aggregator = [
            *aggregation,
            {"$sort": {field: -1}},
            {"$limit": amount + offset}
        ]
        return list(self.connection.dungeons.aggregate(aggregator))[offset:]
    
    def aggregate(self, *, collection : Literal["users", "dungeons", "rooms"], aggregation : list[dict]):
        """
        Aggregate documents.
        """
        return getattr(self.connection, collection).aggregate(aggregation)

























