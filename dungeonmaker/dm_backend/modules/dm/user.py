"""
Submodule for handling users.
"""
from typing import Self
from .dmtypes import BaseUser, UserId
from .session import database_abstraction
from .utils import s_vars




class User(BaseUser):
    """
    Class for handling users.
    """
    @classmethod
    def lookup_user(cls, *, username : str = None, user_id : UserId = None) -> Self:
        """
        Find a user based on its username or user id.
        """
        return cls(**database_abstraction.select_user(user_id=user_id, fields={"username": username} if username else {}))
    
    @classmethod
    def read(cls, user_id : UserId) -> Self:
        """
        Read a user based on its user_id.
        """
        return cls(**database_abstraction.select_user(user_id=user_id))
    
    def write(self):
        """
        Method for writing a user.
        """
        if self.new:
            self.new = False
            database_abstraction.insert_user(data=s_vars(self))
            return
        database_abstraction.update_user(user_id=self.user_id, updator={"$set": s_vars(self)})






























