"""
Submodule for the backend
"""
import pickle, hmac
from hashlib import sha3_256
from types import ModuleType
from typing import Union, Any
from dataclasses import dataclass, field
from scratchcommunication.cloud_socket import CloudSocket
from scratchcommunication.cloud import CloudConnection
from .modules.scratchcomms import RequestHandler
from .modules.database import MongoDBDatabaseAbstraction, MongoDBAtlasSession
from .modules.dm.session import DMSession
from .modules.dm.selectors import DUNGEON, ROOM, USER
from .modules.dm.user import User

@dataclass(slots=True)
class DMBackend:
    db_session : MongoDBAtlasSession = field(kw_only=True)
    db_abstraction : MongoDBDatabaseAbstraction = field(init=False)
    dm_session : DMSession = field(init=False)
    cloud : CloudConnection = field(kw_only=True)
    clients : dict[str, dict[str, Any]] = field(init=False)
    request_handler : RequestHandler = field(init=False)
    
    def __init__(self, *, db_session : MongoDBAtlasSession, cloud : CloudConnection, security : Union[tuple, None] = None):
        self.db_session = db_session
        self.db_abstraction = MongoDBDatabaseAbstraction(connection=db_session)
        self.dm_session = DMSession()
        self.dm_session.add_database_abstraction(self.db_abstraction)
        self.cloud = cloud
        self.request_handler = RequestHandler(cloud_socket=CloudSocket(cloud=cloud, security=security))
        self.clients = {}
        
    def start(self, *, thread=True):
        @self.request_handler.request(name="login", allow_python_syntax=True, auto_convert=True)
        def login(username : str, password : str) -> str:
            passdata = gen_passdata(username=username, password=password)
            try:
                user = self.dm_session.find(USER, name=username)
            except KeyError:
                return "Username doesn't exist."
            if not hmac.compare_digest(passdata, user.passdata):
                self.current_client_data["logged_in"] = self.current_client_data.get("logged_in", False)
                self.current_client_data["username"] = self.current_client_data.get("username", None)
                self.current_client_data["user_id"] = self.current_client_data.get("user_id", None)
                return "Wrong credentials"
            self.current_client_data["logged_in"] = True
            self.current_client_data["username"] = user.username
            self.current_client_data["user_id"] = user.user_id
            return "Success!"
        
        @self.request_handler.request(name="sign_up", allow_python_syntax=True, auto_convert=True)
        def sign_up(username : str, password : str) -> str:
            passdata = gen_passdata(username=username, password=password)
            try:
                user = self.dm_session.find(USER, name=username)
            except KeyError:
                pass
            except Exception as e:
                raise RuntimeError("Some error occured") from e
            else:
                return "Username already exists."
            if len(password) < 3 or len(username) < 3:
                return "Your username and password needs to be at least 3 characters long."
            self.current_client_data["logged_in"] = True
            self.current_client_data["username"] = username
            user = User(username=username, session=self.dm_session, passdata=passdata)
            self.current_client_data["user_id"] = user.user_id
            user.write()
            return "Success!"
                
        
        
        self.request_handler.start(thread=thread)
        
    def stop(self):
        self.request_handler.stop()
        
    @property
    def current_client_data(self) -> dict:
        """
        Client data of the current user
        """
        if not self.request_handler.current_client.client_id in self.clients:
            self.clients[self.request_handler.current_client.client_id] = {}
        return self.clients[self.request_handler.current_client.client_id]
    
    @current_client_data.setter
    def set_current_client_data(self, data : dict):
        self.clients[self.request_handler.current_client.client_id] = data
        
    def find_current_client_user(self) -> User:
        """
        Find the User Account associated with the current user.
        """
        if not self.current_client_data("logged_in", False):
            raise ValueError("User is not logged in")
        return self.dm_session.find(USER, self.current_client_data["user_id"])





def gen_passdata(*, username : str, password : str) -> bytes:
    passdata = sha3_256(pickle.dumps((username, password, "Dungeon Maker: Reinvented - Login System Salt"))).digest()
    return passdata
























