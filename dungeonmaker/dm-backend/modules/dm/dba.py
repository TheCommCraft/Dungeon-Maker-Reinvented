"""
Submodule for database abstractions.
"""
from .dmtypes import UserId, DungeonId, RoomId


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
    
class DatabaseAbstractionSelector(BaseDatabaseAbstraction):
    """
    Class for selecting a database abstraction.
    """
    dbas : list[BaseDatabaseAbstraction]
    
    def __init__(self, dbas : list[BaseDatabaseAbstraction]):
        self.dbas = dbas
        
    def select_user(self, user_id : UserId = None, *, fields : dict = None) -> dict:
        """
        Automatically selects an abstraction to select a user.
        """
        for dba in self.dbas:
            try:
                return dba.select_user(user_id=user_id, fields=fields)
            except NotImplementedError:
                continue
        raise NotImplementedError
    
    def select_dungeon(self, dungeon_id : DungeonId = None, *, fields : dict = None) -> dict:
        """
        Automatically selects an abstraction to select a dungeon.
        """
        for dba in self.dbas:
            try:
                return dba.select_dungeon(dungeon_id=dungeon_id, fields=fields)
            except NotImplementedError:
                continue
        raise NotImplementedError
    
    def select_room(self, room_id : RoomId = None, *, fields : dict = None) -> dict:
        """
        Automatically selects an abstraction to select a room.
        """
        for dba in self.dbas:
            try:
                return dba.select_room(room_id=room_id, fields=fields)
            except NotImplementedError:
                continue
        raise NotImplementedError
    
    def update_user(self, user_id : UserId = None, *, fields : dict = None, updator : dict = None):
        """
        Automatically selects an abstraction to update a user.
        """
        for dba in self.dbas:
            try:
                return dba.update_user(user_id=user_id, fields=fields, updator=updator)
            except NotImplementedError:
                continue
        raise NotImplementedError
    
    def update_dungeon(self, dungeon_id : DungeonId = None, *, fields : dict = None, updator : dict = None):
        """
        Automatically selects an abstraction to update a dungeon.
        """
        for dba in self.dbas:
            try:
                return dba.update_dungeon(dungeon_id=dungeon_id, fields=fields, updator=updator)
            except NotImplementedError:
                continue
        raise NotImplementedError
    
    def update_room(self, room_id : RoomId = None, *, fields : dict = None, updator : dict = None):
        """
        Automatically selects an abstraction to update a room.
        """
        for dba in self.dbas:
            try:
                return dba.update_room(room_id=room_id, fields=fields, updator=updator)
            except NotImplementedError:
                continue
        raise NotImplementedError
    
    def insert_user(self, *, data : dict = None):
        """
        Automatically selects an abstraction to insert a user.
        """
        for dba in self.dbas:
            try:
                return dba.insert_user(data=data)
            except NotImplementedError:
                continue
        raise NotImplementedError

    def insert_dungeon(self, *, data : dict = None):
        """
        Automatically selects an abstraction to insert a dungeon.
        """
        for dba in self.dbas:
            try:
                return dba.insert_dungeon(data=data)
            except NotImplementedError:
                continue
        raise NotImplementedError
    
    def insert_room(self, *, data : dict = None):
        """
        Automatically selects an abstraction to insert a room.
        """
        for dba in self.dbas:
            try:
                return dba.insert_room(data=data)
            except NotImplementedError:
                continue
        raise NotImplementedError
        































