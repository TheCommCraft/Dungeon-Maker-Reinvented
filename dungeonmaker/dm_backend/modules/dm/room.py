"""
Submodule for dungeons.
"""
from typing import Self
from .dmtypes import RoomId, BaseDungeon, BaseRoom
from . import dungeon
from .session import database_abstraction
from .utils import s_vars

class Room(BaseRoom):
    """
    Class for rooms.
    """
    def get_dungeon(self) -> BaseDungeon:
        """
        Get the corresponding dungeon.
        """
        return dungeon.Dungeon.read(self.dungeon_id)
    
    @classmethod
    def read(cls, room_id : RoomId) -> Self:
        """
        Classmethod for reading a room.
        """
        data = database_abstraction.select_room(room_id=room_id)
        return cls(**data)
    
    def write(self):
        """
        Method for writing a room.
        """
        if self.new:
            self.new = False
            database_abstraction.insert_room(data=s_vars(self))
            return
        database_abstraction.update_room(room_id=self.room_id, updator={"$set": s_vars(self)})















