"""
Types used in the dm library
"""
from __future__ import annotations
from typing import Literal, Any, Union, Sequence, Mapping
from weakref import WeakValueDictionary
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





@dataclass(slots=True)
class Permission:
    """
    Class for permissions.
    """
    type: Literal[
        "read", 
        "edit_rooms", 
        "edit_room", 
        "edit_permissions", 
        "edit_infos", 
        "permission_level"
        ] = field(kw_only=True)
    value: Any = field(kw_only=True)



class Permissions(list[Permission]):
    """
    Class for containing a list of permissions.
    """
    def get(self, __type : Any) -> Permission:
        try:
            return ([i for i in self if i.type == __type] + [Permission(type=__type, value=None)])[0]
        except IndexError:
            pass
    
    def get_all(self, __type : Any) -> list[Permission]:
        return [i for i in self if i.type == __type]
        
    def can_edit_room(self, *, room_id : RoomId = None, room : BaseRoom = None):
        room_id = room_id or room.room_id
        if self.get("edit_rooms"):
            return True
        return any(i.value == room_id for i in self.get_all("edit_room"))

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
class BaseDungeonUser:
    """
    Base class for dungeon users.
    """
    user_id : UserId = field(kw_only=True)
    dungeon : BaseDungeon = field(kw_only=True)
    permissions : Permissions = field(kw_only=True)
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
    remaining_dungeons : int = field(kw_only=True, default=16)
    remaining_rooms : int = field(kw_only=True, default=128)
    stats : Stats = field(kw_only=True, default_factory=Stats)



@dataclass(slots=True)
class BaseDungeon:
    """
    Base class for dungeons.
    """
    rooms : list[RoomId] = field(kw_only=True, default_factory=list)
    owner : UserId = field(kw_only=True)
    owner_name : str = field(kw_only=True)
    permissions : dict[UserId, Permissions] = field(kw_only=True, default_factory=dict)
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



@dataclass
class BaseDMSession:
    database_abstractions : list[BaseDatabaseAbstraction] = field(default_factory=list, kw_only=True)
    database_abstraction : BaseDatabaseAbstraction = field(init=False)
    
    def add_database_abstraction(self, dba : BaseDatabaseAbstraction):
        """
        Add a database abstraction.
        """
        raise NotImplementedError


    def get_popular_tab(self, *, offset : int = 0, amount : int = 20) -> list[BaseDungeon]:
        """
        Get a default of 20 dungeons with no offset from the most popular dungeons.
        """
        raise NotImplementedError

    def get_random_tab(self, *, offset : int = 0, amount : int = 20) -> list[BaseDungeon]:
        """
        Get a default of 20 dungeons of random dungeons. 
        """
        raise NotImplementedError

    def get_default_tab(self, *, offset : int = 0, amount : int = 20) -> list[BaseDungeon]:
        """
        Get a default of 20 dungeons of random dungeons. 
        """
        raise NotImplementedError

    def get_newest_tab(self, *, offset : int = 0, amount : int = 20) -> list[BaseDungeon]:
        """
        Get a default of 20 dungeons of the newest dungeons. 
        """
        raise NotImplementedError

    def search_for_term(self, term : str, *, amount : int = 10) -> list[BaseDungeon]:
        """
        Searches for terms.
        """
        raise NotImplementedError

    def find(self, type : Literal["dungeon", "room", "user"], id : Union[DungeonId, RoomId, UserId] = None, *, name : str = None) -> Union[BaseDungeon, BaseRoom, BaseUser]:
        """
        Finds something.
        """
        raise NotImplementedError

    def create(self, type : Literal["dungeon", "room", "user"], *, args : Sequence = (), kwargs : Mapping = {}) -> Union[BaseDungeon, BaseRoom, BaseUser]:
        """
        Creates something.
        """
        raise NotImplementedError







