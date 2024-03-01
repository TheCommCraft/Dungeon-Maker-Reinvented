"""
Submodule for handling users.
"""
from .dmtypes import BaseUser, UserId





class User(BaseUser):
    @classmethod
    def lookup_user(cls, *, username : str = None, user_id : UserId = None):
        """
        Find a user based on its username or user id.
        """
        raise NotImplementedError
    
    @classmethod
    def read(cls, user_id : UserId):
        raise NotImplementedError






























