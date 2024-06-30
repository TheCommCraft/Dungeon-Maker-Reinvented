"""
Submodule for dungeons.
"""
from __future__ import annotations
from typing import Self
from .dmtypes import RoomId, BaseDungeon, BaseRoom, UserId
from . import dungeon, user
from . import session as _session
from .utils import s_vars
from .selectors import DUNGEON

class Room(BaseRoom):
    """
    Class for rooms.
    """
    def get_dungeon(self) -> BaseDungeon:
        """
        Get the corresponding dungeon.
        """
        return dungeon.Dungeon.read(self.dungeon_id, session=self.session)
    
    @classmethod
    def read(cls, room_id : RoomId, *, session : _session.DMSession) -> Self:
        """
        Classmethod for reading a room.
        """
        data = session.database_abstraction.select_room(room_id=room_id)
        return cls(**data)
    
    def write(self):
        """
        Method for writing a room.
        """
        if self.new:
            self.new = False
            self.session.database_abstraction.insert_room(data=s_vars(self))
            return
        self.session.database_abstraction.update_room(room_id=self.room_id, updator={"$set": s_vars(self)})
        
    def get_dungeon(self):
        """
        Get the corresponding dungeon.
        """
        return self.session.find(DUNGEON, self.dungeon_id)
    
    def can_be_edited(self, *, user : user.User = None, user_id : UserId) -> bool:
        """
        Return whether a certain user can edit a room.
        """
        user_id = user_id or user.user_id
        __dungeon = self.get_dungeon()
        return __dungeon.permissions[user_id].can_edit_room(self.room_id)














