"""
Submodule for dungeons.
"""
from .dmtypes import RoomId, BaseDungeon, BaseRoom
from . import dungeon

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
    def read(self, room_id : RoomId):
        raise NotImplementedError
















