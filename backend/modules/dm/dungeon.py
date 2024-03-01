"""
Submodule for dungeons.
"""
from .dmtypes import DungeonId, BaseDungeon, BaseRoom, UserId, Permition, RoomId, BaseDungeonUser
from . import room

class Dungeon(BaseDungeon):
    """
    Class for dungeons.
    """
    def __init__(
        self, 
        *, 
        views : int = 0, 
        likers : list[UserId] = None, 
        owner : UserId, 
        permitions : dict[UserId, list[Permition]] = None, 
        rooms : list[RoomId]
    ):
        self.views = views
        self.likers = list(likers or ())
        self.owner = owner
        self.permitions = dict(permitions or {})
        self.rooms = rooms
    
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
        return [room.Room.read(room_id) for room_id in self.rooms]
    
    def get_user(self, username : str = None, *, user_id : UserId = None) -> BaseDungeonUser:
        """
        Get a user of the dungeon.
        """
        user_id = user_id or username
        permitions = self.permitions.get(user_id, [])
        owner = self.owner == user_id
        return DungeonUser(user_id=user_id, permitions=permitions, owner=owner, dungeon=self)
        
    
    @classmethod
    def read(self, dungeon_id : DungeonId):
        raise NotImplementedError

class DungeonUser(BaseDungeonUser):
    """
    Class for handling users in the context of a dungeon.
    """
    














