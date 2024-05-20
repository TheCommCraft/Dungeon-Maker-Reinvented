"""
Submodule for database connection.
"""
import random
from typing import Literal, Union, assert_never, Sequence, Mapping

from dataclasses import dataclass, field
from . import dungeon, user, room
from . import dba as _dba
from .dmtypes import DungeonId, RoomId, UserId, BaseDatabaseAbstraction
from .selectors import DUNGEON, ROOM, USER

@dataclass
class DMSession:

    def __init__(self, *, database_abstractions : list = None):
        self.database_abstractions = list(database_abstractions or ())
        self.database_abstraction = _dba.DatabaseAbstractionSelector(self.database_abstractions)

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

    def find(self, type : Literal["dungeon", "room", "user"], id : Union[DungeonId, RoomId, UserId] = None, *, name : str = None) -> Union[dungeon.Dungeon, room.Room, user.User]:
        """
        Finds something.
        """
        if type == DUNGEON:
            return dungeon.Dungeon.read(dungeon_id=id, session=self)
        if type == ROOM:
            return room.Room.read(id, session=self)
        if type == USER:
            return user.User.lookup_user(user_id=id, username=name, session=self)
        assert_never(type)

    def create(self, type : Literal["dungeon", "room", "user"], *, args : Sequence = (), kwargs : Mapping = {}) -> Union[dungeon.Dungeon, room.Room, user.User]:
        """
        Creates something.
        """
        args = list(args)
        kwargs = dict(kwargs)
        if type == DUNGEON:
            return dungeon.Dungeon(*args, session=self, **kwargs)
        if type == ROOM:
            return room.Room(*args, session=self, **kwargs)
        if type == USER:
            return user.User(*args, session=self, **kwargs)
        assert_never(type)

















