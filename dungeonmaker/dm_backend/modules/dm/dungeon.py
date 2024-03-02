"""
Submodule for dungeons.
"""
import time, copy
from typing import Self
from .dmtypes import (
    DungeonId, 
    BaseDungeon, 
    BaseRoom, 
    UserId, 
    Permition, 
    BaseDungeonUser, 
    Permitions
)
from .room import Room
from .user import User
from . import room
from .session import database_abstraction
from .utils import s_vars

class Dungeon(BaseDungeon):
    """
    Class for dungeons.
    """
    def __init__(self, *args, **kwargs):
        kwargs["permitions"] = kwargs.get("permitions", {})
        kwargs["permitions"][kwargs["owner"]] = Permitions([
            Permition(type="read", value=True),
            Permition(type="edit_rooms", value=True),
            Permition(type="edit_infos", value=True),
            Permition(type="edit_permitions", value=True),
            Permition(type="permition_level", value=999),
        ])
        super().__init__(*args, **kwargs)
    
    @property
    def likes(self) -> int:
        """
        Amount of likes.
        """
        return len(self.likers)
    
    def get_rooms(self) -> list[BaseRoom]:
        """
        Get corresponding rooms.
        """
        return [room.Room.read(room_id=room_id) for room_id in self.rooms]
    
    def get_user(self, username : str = None, *, user_id : UserId = None) -> BaseDungeonUser:
        """
        Get a user of the dungeon.
        """
        user_id = user_id or User.lookup_user(username=username).user_id
        permitions = self.permitions.get(user_id, Permitions([Permition(type="read", value=True)]))
        owner = self.owner == user_id
        d_user = DungeonUser(user_id=user_id, permitions=permitions, owner=owner, dungeon=self)
        self.permitions[user_id] = d_user
        return d_user
        
    
    @classmethod
    def read(cls, dungeon_id : DungeonId) -> Self:
        """
        Method for reading a dungeon.
        """
        return cls(**database_abstraction.select_dungeon(dungeon_id=dungeon_id))
    
    def write(self):
        """
        Method for writing a dungeon.
        """
        data = copy.deepcopy(s_vars(self))
        for _, perms in (data["permitions"]).items():
            perms[:] = [{"type": perm.type, "value": perm.value} for perm in perms]
        if self.new:
            self.new = False
            database_abstraction.insert_dungeon(data=data)
            return
        database_abstraction.update_dungeon(dungeon_id=self.dungeon_id, updator={"$set": data})
        
    def new_room(self, content : str = None) -> Room:
        """
        Method for creating a new room.
        """
        new_room = Room(content=content, dungeon_id=self.dungeon_id, new=True)
        self.rooms.append(new_room.room_id)
        return new_room
    
    def log_update(self):
        self.update_time = time.time()

class DungeonUser(BaseDungeonUser):
    """
    Class for handling users in the context of a dungeon.
    """














