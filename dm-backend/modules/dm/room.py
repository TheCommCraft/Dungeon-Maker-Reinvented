"""
Submodule for dungeons.
"""
from .dmtypes import RoomId, BaseDungeon, BaseRoom
from . import dungeon
from . import session

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
    def read(cls, room_id : RoomId):
        data = session.database_abstraction.select_room(room_id=room_id)
        return cls(room_id=data["room_id"], dungeon_id=data["dungeon_id"], content=data["content"])
    
    def write(self):
        session.database_abstraction.update_room(room_id=self.room_id, updator={"content": self.content})















