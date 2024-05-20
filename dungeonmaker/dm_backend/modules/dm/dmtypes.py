"""
Types used in the dm library
"""
from typing import Literal, Any, Union
from dataclasses import dataclass, field
import secrets, time



RoomId = int

DungeonId = int

UserId = str

class BaseDatabaseAbstraction:
    """
    Base class for database abstractions.
    """
    def select_user(self, user_id : UserId = None, *, fields : dict = None) -> dict:
        """
        Do not use.
        """
        raise NotImplementedError
    
    def select_dungeon(self, dungeon_id : DungeonId = None, *, fields : dict = None) -> dict:
        """
        Do not use.
        """
        raise NotImplementedError
    
    def select_room(self, room_id : RoomId = None, *, fields : dict = None) -> dict:
        """
        Do not use.
        """
        raise NotImplementedError
    
    def update_user(self, user_id : UserId = None, *, fields : dict = None, updator : dict = None):
        """
        Do not use.
        """
        raise NotImplementedError
    
    def update_dungeon(self, dungeon_id : DungeonId = None, *, fields : dict = None, updator : dict = None):
        """
        Do not use.
        """
        raise NotImplementedError
    
    def update_room(self, room_id : RoomId = None, *, fields : dict = None, updator : dict = None):
        """
        Do not use.
        """
        raise NotImplementedError
    
    def insert_user(self, *, data : dict = None):
        """
        Do not use.
        """
        raise NotImplementedError
    
    def insert_dungeon(self, *, data : dict = None):
        """
        Do not use.
        """
        raise NotImplementedError
    
    def insert_room(self, *, data : dict = None):
        """
        Do not use.
        """
        raise NotImplementedError
    
    def random_dungeons(self, *, amount : int = 1) -> list[dict]:
        """
        Do not use.
        """
        raise NotImplementedError
    
    def sorted_dungeons(
        self, 
        *, 
        amount : int = 20, 
        offset : int = 0,
        field : str = "score", 
        aggregation : list[dict] = [{"$addFields":{"score": {"$add": [{"$multiply": [20,{"$size": "$likers"},]},"$views"]}}}]
    ) -> list[dict]:
        """
        Do not use.
        """
        raise NotImplementedError

@dataclass
class BaseDMSession:
    database_abstractions : list[BaseDatabaseAbstraction] = field(default_factory=list, kw_only=True)
    database_abstraction : BaseDatabaseAbstraction = field(init=False)


@dataclass(slots=True)
class Permition:
    """
    Class for permitions.
    """
    type: Literal[
        "read", 
        "edit_rooms", 
        "edit_room", 
        "edit_permitions", 
        "edit_infos", 
        "permition_level"
        ] = field(kw_only=True)
    value: Any = field(kw_only=True)



class Permitions(list[Permition]):
    """
    Class for containing a list of permitions.
    """
    def get(self, __type : Any) -> Permition:
        try:
            return ([i for i in self if i.type == __type] + [Permition(type=__type, value=None)])[0]
        except IndexError:
            pass



class Stats(dict):
    """
    Class for statistics.
    """




@dataclass(slots=True)
class BaseRoom:
    """
    Base class for rooms.
    """
    room_id : RoomId = field(kw_only=True, default_factory=lambda : secrets.randbits(32))
    dungeon_id : DungeonId = field(kw_only=True)
    content : Any = field(kw_only=True, default=None)
    new : bool = field(kw_only=True, default=True)
    _id : Any = field(kw_only=True, default=None)
    session : BaseDMSession = field(kw_only=True)




@dataclass(slots=True)
class BaseDungeon:
    """
    Base class for dungeons.
    """
    rooms : list[RoomId] = field(kw_only=True, default_factory=list)
    owner : UserId = field(kw_only=True)
    owner_name : str = field(kw_only=True)
    permitions : dict[UserId, Permitions] = field(kw_only=True, default_factory=dict)
    views : int = field(kw_only=True, default=0)
    likers : list[UserId] = field(kw_only=True, default_factory=list)
    new : bool = field(kw_only=True, default=True)
    dungeon_id : DungeonId = field(kw_only=True, default_factory=lambda : secrets.randbits(32))
    name : str = field(kw_only=True)
    description : str = field(kw_only=True)
    creation_time : float = field(kw_only=True, default_factory=time.time)
    update_time : float = field(kw_only=True, default_factory=time.time)
    _id : Any = field(kw_only=True, default=None)
    score : Any = field(kw_only=True, default=None)
    session : BaseDMSession = field(kw_only=True)
    stats : Stats = field(kw_only=True, default_factory=Stats)
    start : tuple = field(kw_only=True)




@dataclass(slots=True)
class BaseDungeonUser:
    """
    Base class for dungeon users.
    """
    user_id : UserId = field(kw_only=True)
    dungeon : BaseDungeon = field(kw_only=True)
    permitions : Permitions = field(kw_only=True)
    owner : bool = field(kw_only=True)


@dataclass(slots=True)
class BaseUser:
    """
    Base class for users.
    """
    user_id : UserId = field(kw_only=True, default_factory=lambda : str(secrets.randbits(32)))
    owned_dungeons : list[DungeonId] = field(kw_only=True, default_factory=list)
    recent_dungeons : list[DungeonId] = field(kw_only=True, default_factory=list)
    permitted_dungeons : list[DungeonId] = field(kw_only=True, default_factory=list)
    username : str = field(kw_only=True)
    admin_level : int = field(kw_only=True, default=0)
    new : bool = field(kw_only=True, default=True)
    _id : Any = field(kw_only=True, default=None)
    session : BaseDMSession = field(kw_only=True)
    passdata : bytes = field(kw_only=True)
    linked_user : Union[str, None] = field(kw_only=True, default=None)
    stats : Stats = field(kw_only=True, default_factory=Stats)












