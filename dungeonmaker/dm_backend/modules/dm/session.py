"""
Submodule for database connection.
"""
from __future__ import annotations
import random
from weakref import WeakValueDictionary
from typing import Literal, Union, assert_never, Sequence, Mapping
from dataclasses import dataclass, field
from . import dungeon, user, room
from . import dba as _dba
from .dmtypes import DungeonId, RoomId, UserId, BaseDatabaseAbstraction
from .selectors import DUNGEON, ROOM, USER

@dataclass
class DMSession:
    database_abstraction : _dba.DatabaseAbstractionSelector
    database_abstractions : list[BaseDatabaseAbstraction]
    _cached : dict[WeakValueDictionary[str, Union[dungeon.Dungeon, user.User, room.Room]]]

    def __init__(self, *, database_abstractions : list = None):
        self.database_abstractions = list(database_abstractions or ())
        self.database_abstraction = _dba.DatabaseAbstractionSelector(self.database_abstractions)
        self.setup_cache()
        
    def setup_cache(self):
        self._cached = {}
        self._cached["dungeons"] = WeakValueDictionary()
        self._cached["users"] = WeakValueDictionary()
        self._cached["rooms"] = WeakValueDictionary()
        

    def add_database_abstraction(self, dba : BaseDatabaseAbstraction):
        """
        Add a database abstraction.
        """
        assert isinstance(dba, BaseDatabaseAbstraction)
        self.database_abstractions.append(dba)


    def get_popular_tab(self, *, offset : int = 0, amount : int = 20) -> list[dungeon.Dungeon]:
        """
        Get a default of 20 dungeons with no offset from the most popular dungeons.
        """
        return [dungeon.Dungeon(**dungeon_data) for dungeon_data in self.database_abstraction.sorted_dungeons(offset=offset, amount=amount)]

    def get_random_tab(self, *, offset : int = 0, amount : int = 20) -> list[dungeon.Dungeon]:
        """
        Get a default of 20 dungeons of random dungeons. 
        """
        return [dungeon.Dungeon(**dungeon_data) for dungeon_data in self.database_abstraction.random_dungeons(amount=amount)]

    def get_default_tab(self, *, offset : int = 0, amount : int = 20) -> list[dungeon.Dungeon]:
        """
        Get a default of 20 dungeons of random dungeons. 
        """
        data = [dungeon.Dungeon(**dungeon_data) for dungeon_data in self.database_abstraction.sorted_dungeons(amount=3*amount, aggregation=[{"$sample": {"size": amount * 3}}, {"$addFields": {"score": {"$add": [{"$multiply": [20, {"$size": "$likers" }] }, "$views"]}}}])]
        return data[:amount // 2] + random.sample(data[amount // 2:], min(len(data[amount // 2:]), amount - amount // 2))

    def get_newest_tab(self, *, offset : int = 0, amount : int = 20) -> list[dungeon.Dungeon]:
        """
        Get a default of 20 dungeons of the newest dungeons. 
        """
        return [dungeon.Dungeon(**dungeon_data) for dungeon_data in self.database_abstraction.sorted_dungeons(offset=offset, amount=amount, field="creation_time", aggregation=[])]

    def search_for_term(self, term : str, *, amount : int = 10) -> list[dungeon.Dungeon]:
        """
        Searches for terms.
        """
        aggregator = [
            {
                "$search": {
                    "index": "namesearch",
                    "text": {
                        "query": term,
                        "path": {
                            "wildcard": "*"
                        },
                        "fuzzy": {
                            "maxEdits": 2,
                            "maxExpansions": 2
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "score": {
                        "$add": [
                            {"$multiply":
                                [
                                    20, {"$size": "$likers" }
                                ]
                            },
                            "$views"
                        ]
                    }
                }
            }
        ]
        return [dungeon.Dungeon(**dungeon_data) for dungeon_data in self.database_abstraction.sorted_dungeons(amount=amount, field="score", aggregation=aggregator)]

    def lookup_cache(self, cache_type : str, __id : Union[DungeonId, RoomId, UserId]) -> Union[None, dungeon.Dungeon, room.Room, user.User]:
        """
        Don't use.
        """
        if __id in (cache := self._cached[cache_type]):
            return cache[__id]
        
    def save_cache(self, cache_type : str, __id : Union[DungeonId, RoomId, UserId], value : Union[dungeon.Dungeon, room.Room, user.User]):
        """
        Don't use.
        """
        self._cached[cache_type][__id] = value

    def find(self, __type : Literal["dungeon", "room", "user"], __id : Union[DungeonId, RoomId, UserId] = None, *, name : str = None) -> Union[dungeon.Dungeon, room.Room, user.User]:
        """
        Finds something.
        """
        if __type == DUNGEON:
            if (value := self.lookup_cache("dungeons", __id)):
                return value
            __dungeon = dungeon.Dungeon.read(dungeon_id=__id, session=self)
            self.save_cache("dungeons", __id, __dungeon)
            return __dungeon
        if __type == ROOM:
            if (value := self.lookup_cache("rooms", __id)):
                return value
            __room = room.Room.read(__id, session=self)
            self.save_cache("rooms", __id, __room)
            return __room
        if __type == USER:
            if (value := self.lookup_cache("users", __id)):
                return value
            __user = user.User.lookup_user(user_id=__id, username=name, session=self)
            self.save_cache("users", __id, __user)
            return __user
        assert_never(__type)

    def create(self, __type : Literal["dungeon", "room", "user"], *, args : Sequence = (), kwargs : Mapping = None) -> Union[dungeon.Dungeon, room.Room, user.User]:
        """
        Creates something.
        """
        kwargs = kwargs or {}
        if __type == DUNGEON:
            __dungeon = dungeon.Dungeon(*args, session=self, **kwargs)
            __id = __dungeon.dungeon_id
            if self.lookup_cache("dungeons", __id):
                raise ValueError("Dungeon already exists (in cache!!)")
            self.save_cache("dungeons", __id, __dungeon)
            return __dungeon
        if __type == ROOM:
            __room = room.Room(*args, session=self, **kwargs)
            __id = __room.room_id
            if self.lookup_cache("rooms", __id):
                raise ValueError("Room already exists (in cache!!)")
            self.save_cache("rooms", __id, __room)
            return __room
        if __type == USER:
            __user = user.User(*args, session=self, **kwargs)
            __id = __user.user_id
            if self.lookup_cache("users", __id):
                raise ValueError("User already exists (in cache!!)")
            self.save_cache("users", __id, __user)
            return __user
        assert_never(__type)

















