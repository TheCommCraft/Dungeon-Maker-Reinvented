"""
Types used in the dm library
"""
from typing import Literal, Any
from dataclasses import dataclass, field
import secrets, time






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



class Permitions(list[Permition]):
    """
    Class for containing a list of permitions.
    """
    def get(self, __type : Any) -> Permition:
        return ([i for i in self if i.type == __type] + [Permition(type=__type, value=None)])[0]






@dataclass(slots=True)
class BaseRoom:
    """
    Base class for rooms.
    """
    room_id : RoomId = field(kw_only=True, default_factory=lambda : secrets.randbits(32))
    dungeon_id : DungeonId = field(kw_only=True)
    content : Any = field(kw_only=True, default=None)
    new : bool = field(kw_only=True, default=False)
    _id : Any = field(kw_only=True, default=None)




@dataclass(slots=True)
class BaseDungeon:
    """
    Base class for dungeons.
    """
    rooms : list[RoomId] = field(kw_only=True)
    owner : UserId = field(kw_only=True)
    permitions : dict[UserId, Permitions] = field(kw_only=True)
    views : int = field(kw_only=True)
    likers : list[UserId] = field(kw_only=True, default_factory=list)
    new : bool = field(kw_only=True, default=False)
    dungeon_id : DungeonId = field(kw_only=True, default_factory=lambda : secrets.randbits(32))
    name : str = field(kw_only=True)
    description : str = field(kw_only=True)
    creation_time : float = field(kw_only=True, default_factory=time.time)
    update_time : float = field(kw_only=True, default_factory=time.time)
    _id : Any = field(kw_only=True, default=None)
    score : Any = field(kw_only=True, default=None)




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
    user_id : UserId = field(kw_only=True, default_factory=lambda : secrets.randbits(32))
    owned_dungeons : list[DungeonId] = field(kw_only=True)
    recent_dungeons : list[DungeonId] = field(kw_only=True)
    permitted_dungeons : list[DungeonId] = field(kw_only=True)
    username : str = field(kw_only=True)
    admin_level : int = field(kw_only=True)
    new : bool = field(kw_only=True, default=False)
    _id : Any = field(kw_only=True, default=None)













