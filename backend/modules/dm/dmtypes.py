"""
Types used in the dm library
"""
from typing import Literal, Any
from dataclasses import dataclass, field
import json


type RoomId = int

type DungeonId = int

type UserId = str

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

    def encode(self) -> str:
        """
        Encode a permition.
        """
        return json.dumps({"type": self.type, "value": self.value})

    @classmethod
    def decode(cls, string : str):
        """
        Decode a permition.
        """
        return cls(*json.loads(string))



class Permitions(list[Permition]):
    """
    Class for containing a list of permitions.
    """
    def get(self, type):
        return [i for i in self if i.type == type][0]





@dataclass(slots=True)
class BaseRoom:
    """
    Base class for rooms.
    """
    room_id : RoomId = field(kw_only=True)
    dungeon_id : DungeonId = field(kw_only=True)




@dataclass(slots=True)
class BaseDungeon:
    """
    Base class for dungeons.
    """
    rooms : list[RoomId] = field(kw_only=True)
    owner : UserId = field(kw_only=True)
    permitions : dict[UserId, list[Permition]] = field(kw_only=True)
    views : int = field(kw_only=True)
    likers : list[UserId] = field(kw_only=True)
    




@dataclass(slots=True)
class BaseDungeonUser:
    """
    Base class for dungeon users.
    """
    user_id : UserId = field(kw_only=True)
    dungeon : BaseDungeon = field(kw_only=True)
    permitions : list[Permition] = field(kw_only=True)
    owner : bool = field(kw_only=True)


@dataclass(slots=True)
class BaseUser:
    """
    Base class for users.
    """
    user_id : UserId = field(kw_only=True)
    owned_dungeons : list[DungeonId] = field(kw_only=True)
    recent_dungeons : list[DungeonId] = field(kw_only=True)
    permitted_dungeons : list[DungeonId] = field(kw_only=True)
    username : str = field(kw_only=True)
    admin_level : int = field(kw_only=True)













