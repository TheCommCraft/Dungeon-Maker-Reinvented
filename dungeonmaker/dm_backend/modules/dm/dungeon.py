"""
Submodule for dungeons.
"""
from __future__ import annotations
import time, copy, secrets
from typing import Self
from .dmtypes import (
    DungeonId, 
    BaseDungeon, 
    BaseRoom, 
    UserId, 
    RoomId, 
    Permission, 
    BaseDungeonUser, 
    Permissions
)
from .room import Room
from .user import User
from . import room
from . import session as _session
from .utils import s_vars
from .selectors import ROOM

class Dungeon(BaseDungeon):
    """
    Class for dungeons.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("permissions", {})
        kwargs["permissions"][kwargs["owner"]] = Permissions([
            Permission(type="read", value=True),
            Permission(type="edit_rooms", value=True),
            Permission(type="edit_infos", value=True),
            Permission(type="edit_permissions", value=True),
            Permission(type="permission_level", value=999),
        ])
        kwargs["owner_name"] = User.read(kwargs["owner"], session=kwargs["session"]).username
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
        user_id = user_id or User.lookup_user(username=username, session=self.session).user_id
        permissions = self.permissions.get(user_id, Permissions([Permission(type="read", value=True)]))
        owner = self.owner == user_id
        d_user = DungeonUser(user_id=user_id, permissions=permissions, owner=owner, dungeon=self)
        self.permissions[user_id] = d_user
        return d_user
        
    
    @classmethod
    def read(cls, dungeon_id : DungeonId, *, session : _session.DMSession) -> Self:
        """
        Method for reading a dungeon.
        """
        data = session.database_abstraction.select_dungeon(dungeon_id=dungeon_id)
        return cls(**data)
    
    def write(self):
        """
        Method for writing a dungeon.
        """
        data = copy.deepcopy(s_vars(self))
        data["new"] = False
        for _, perms in (data["permissions"]).items():
            perms[:] = [{"type": perm.type, "value": perm.value} for perm in perms]
        if self.new:
            self.new = False
            self.session.database_abstraction.insert_dungeon(data=data)
            return
        self.session.database_abstraction.update_dungeon(dungeon_id=self.dungeon_id, updator={"$set": data})
        
    def new_room(self, *, content : str = None, room_id : RoomId = None) -> Room:
        """
        Method for creating a new room.
        """
        new_room = self.session.create(ROOM, kwargs={"content": content, "dungeon_id": self.dungeon_id, "room_id": room_id or secrets.randbits(32)})
        self.rooms.append(new_room.room_id)
        return new_room
    
    def log_update(self):
        """
        Log an update.
        """
        self.update_time = time.time()
        
    def like(self, user : User):
        """
        Register a like.
        """
        if user.user_id in self.likers:
            return
        self.likers.append(user.user_id)
        
    def unlike(self, user : User):
        """
        Register an unlike.
        """
        if not user.user_id in self.likers:
            return
        self.likers.remove(user.user_id)
        
    def view(self):
        """
        Register a view.
        """
        self.views += 1
        
    def to_object(self) -> dict:
        """
        Convert to an object.
        """
        data = copy.deepcopy(s_vars(self))
        data.pop("rooms")
        data.pop("permissions")
        data.pop("new")
        data.pop("creation_time")
        data.pop("update_time")
        data.pop("score")
        data.pop("stats")
        data.pop("start")
        data.pop("likers")
        data["likes"] = self.likes
        return data
        

class DungeonUser(BaseDungeonUser):
    """
    Class for handling users in the context of a dungeon.
    """














