"""
Submodule for the backend
"""
import pickle, hmac, json, secrets
from hashlib import sha3_256
from types import ModuleType
from typing import Union, Any
from dataclasses import dataclass, field
from scratchcommunication.cloud_socket import CloudSocket
from scratchcommunication.cloud import CloudConnection
from scratchcommunication.cloudrequests import RequestHandler, ErrorMessage
from scratchattach import get_project, Project
from .modules.database import MongoDBDatabaseAbstraction, MongoDBAtlasSession
from .modules.dm.session import DMSession
from .modules.dm.selectors import DUNGEON, ROOM, USER
from .modules.dm.user import User, s_vars
from .modules.dm.dmtypes import RoomId, DungeonId, UserId
from .modules.dm.dungeon import Dungeon, DungeonUser
from .modules.dm.room import Room

@dataclass(slots=True)
class DMBackend:
    """
    Class for the Dungeon Maker Reinvented backend.
    """
    db_session : MongoDBAtlasSession = field(kw_only=True)
    db_abstraction : MongoDBDatabaseAbstraction = field(init=False)
    dm_session : DMSession = field(init=False)
    cloud : CloudConnection = field(kw_only=True)
    clients : dict[str, dict[str, Any]] = field(init=False)
    request_handler : RequestHandler = field(init=False)
    project_id : int = field(kw_only=True)
    project : Project = field(init=False)
    
    def __init__(self, *, db_session : MongoDBAtlasSession, cloud : CloudConnection, project_id : int, security : Union[tuple, None] = None):
        self.db_session = db_session
        self.db_abstraction = MongoDBDatabaseAbstraction(connection=db_session)
        self.dm_session = DMSession()
        self.dm_session.add_database_abstraction(self.db_abstraction)
        self.cloud = cloud
        self.request_handler = RequestHandler(cloud_socket=CloudSocket(cloud=cloud, security=security))
        self.clients = {}
        self.project_id = project_id
        self.project = get_project(project_id)
        
    def run(self, *, thread : bool = True, duration : Union[float, int, None] = None):
        """
        Run the program.
        """
        @self.request_handler.request(name="login", allow_python_syntax=True, auto_convert=True)
        def login(username : str, password : str) -> str:
            user : User
            passdata = gen_passdata(username=username, password=password)
            try:
                user = self.dm_session.find(USER, name=username)
            except KeyError:
                raise ErrorMessage("Username doesn't exist.")
            if not hmac.compare_digest(passdata, user.passdata):
                self.current_client_data.setdefault("logged_in", False)
                self.current_client_data.setdefault("username", None)
                self.current_client_data.setdefault("user_id", None)
                raise ErrorMessage("Wrong credentials")
            self.current_client_data["logged_in"] = True
            self.current_client_data["username"] = user.username
            self.current_client_data["user_id"] = user.user_id
            return "Success!"
        
        @self.request_handler.request(name="sign_up", allow_python_syntax=True, auto_convert=True)
        def sign_up(username : str, password : str, linked_user : str = None) -> str:
            user : User
            passdata = gen_passdata(username=username, password=password)
            try:
                user = self.dm_session.find(USER, name=username)
            except KeyError:
                pass
            except Exception as e:
                raise RuntimeError("Some error occured") from e
            else:
                raise ErrorMessage("Username already exists.")
            if len(password) < 3 or len(username) < 3:
                raise ErrorMessage("Your username and password needs to be at least 3 characters long.")
            self.current_client_data["logged_in"] = True
            self.current_client_data["username"] = username
            linked_user = linked_user.lower()
            if linked_user:
                has_linked = user_has_linked(session=self.dm_session, user=linked_user)
                if has_linked:
                    raise ErrorMessage(f"You already have an account linked: {has_linked['username']}")
                project = self.project
                user = linked_user
                comment = f"My account: {username}"
                if not find_comment(project, content=comment, user=user):
                    raise ErrorMessage(f"Couldn't link your new account to your scratch username. Try commenting \"{comment}\" on the project again.")
            else:
                project = self.project
                comment = f"My account: {username}"
                if not find_comment(project=project, content=comment):
                    raise ErrorMessage(f"Couldn't verify your username. Try commenting \"{comment}\" on the project again.")
            user = self.dm_session.create(USER, kwargs={"username": username, "passdata": passdata, "linked_user": linked_user})
            self.current_client_data["user_id"] = user.user_id
            user.write()
            return "Success!"
        
        @self.request_handler.request(name="load_private_profile", allow_python_syntax=True, auto_convert=True)
        def load_private_profile() -> json.dumps:
            self.ensure_login()
            user_data = s_vars(self.find_current_client_user())
            user_data = include_data(user_data, include=
                [
                    "username", 
                    "user_id",
                    "admin_level",
                    "linked_user",
                    "recent_dungeons",
                    "owned_dungeons",
                    "permitted_dungeons",
                    "passdata"
                ]
            )
            user_data["passdata"] = "maybe not"
            return {"success": True, "result": user_data, "reason": "success"}
                
        @self.request_handler.request(name="load_profile", allow_python_syntax=True, auto_convert=True)
        def load_profile(username : str = None, *, user_id : str = None) -> json.dumps:
            user : User
            try:
                user = self.dm_session.find(USER, id=user_id, name=username)
            except KeyError:
                raise ErrorMessage(json.dumps({"success": False, "result": None, "reason": "That profile doesn't seem to exist."}))
            user_data = s_vars(user)
            user_data = include_data(user_data, include=
                [
                    "username", 
                    "user_id",
                    "admin_level",
                    "linked_user",
                    "recent_dungeons",
                    "owned_dungeons",
                    "permitted_dungeons"
                ]
            )
            return {"success": True, "result": user_data, "reason": "success"}
        
        @self.request_handler.request(name="link_user", allow_python_syntax=True, auto_convert=True)
        def link_user(linked_user : str, password : str) -> str:
            user : User
            self.ensure_login()
            linked_user = linked_user.lower()
            has_linked = user_has_linked(session=self.dm_session, user=linked_user)
            if has_linked:
                raise ErrorMessage(f"You already have an account linked: {has_linked['username']}")
            user = self.find_current_client_user()
            passdata = gen_passdata(username=self.current_client_data["username"], password=password)
            if passdata != user.passdata:
                raise ErrorMessage("Wrong password.")
            project = self.project
            username = self.current_client_data["username"]
            comment = f"My account: {username}"
            user = linked_user
            if not find_comment(project=project, user=user):
                raise ErrorMessage(f"Couldn't link your new account to your scratch username. Try commenting \"{comment}\" on the project again.")
            user.linked_user = linked_user
            user.write()
            return "Success!"
        
        @self.request_handler.request(name="unlink_user", allow_python_syntax=True, auto_convert=True)
        def unlink_user(password : str) -> str:
            user : User
            self.ensure_login
            user = self.find_current_client_user()
            passdata = gen_passdata(username=self.current_client_data["username"], password=password)
            if passdata != user.passdata:
                raise ErrorMessage("Wrong password.")
            user.linked_user = None
            user.write()
            return "Success!"
        
        @self.request_handler.request(name="reset_password", allow_python_syntax=True, auto_convert=True)
        def reset_password(username : str, password : str = None, linked_user : str = None, code : int = None) -> str:
            user : User
            if code is None:
                code = secrets.randbits(24)
                self.current_client_data["password_reset_code"] = code
                return f"Your password reset code is \"{code}\". Try commenting \"Password reset code: {code}\" using your linked account."
            if code != self.current_client_data["password_reset_code"]:
                raise ErrorMessage("Wrong code.")
            user = self.dm_session.find(USER, name=username)
            if linked_user != user.linked_user:
                if user.linked_user is None:
                    raise ErrorMessage("You do not have a user linked, so you cannot reset your password like this. Try commenting on the project for help.")
                raise ErrorMessage("That is not your linked user.")
            project = self.project
            comment = f"Password reset code: {code}"
            user = linked_user
            if not find_comment(project, content=comment, user=user):
                raise ErrorMessage(f"Couldn't verify your password reset request. Try commenting \"{comment}\" on the project again.")
            passdata = gen_passdata(username=username, password=password)
            user.passdata = passdata
            user.write()
            return "Success!"
        
        @self.request_handler.request(name="logout", allow_python_syntax=True, auto_convert=True)
        def logout() -> str:
            self.current_client_data["logged_in"] = False
            self.current_client_data["username"] = None
            self.current_client_data["user_id"] = None
            return "OK"
        
        @self.request_handler.request(name="save_dungeon", allow_python_syntax=True, auto_convert=True)
        def save_dungeon(start_room : RoomId, start_x : int, start_y : int, name : str, dungeon_id=None):
            dungeon : Dungeon
            self.ensure_login()
            try:
                dungeon = self.dm_session.find(DUNGEON, dungeon_id)
            except KeyError:
                dungeon_id = dungeon_id or secrets.randbits(32)
                dungeon = self.dm_session.create(Dungeon, kwargs={
                    "description": "", 
                    "name": name, 
                    "owner": self.current_client_data["user_id"],
                    "owner_name": self.current_client_data["username"],
                    "start": ()
                })
            if not dungeon.get_user(self.current_client_data["username"]).permitions.get("edit_infos"):
                raise ErrorMessage("Not Authorized")
            #if not find_comment(self.pr)
            dungeon.name = name
            dungeon.start = (start_room, start_x, start_y)
            dungeon.write()
            
        @self.request_handler.request(name="save_dungeon_infos", allow_python_syntax=True, auto_convert=True)
        def save_dungeon_infos(dungeon_id)
        
        @self.request_handler.request(name="save_room", allow_python_syntax=True, auto_convert=True)
        def save_room(room_id : RoomId, content : str, bound_dungeon : DungeonId) -> str:
            room : Room
            dungeon : Dungeon
            self.ensure_login()
            try:
                room = self.dm_session.find(ROOM, room_id)
            except KeyError:
                dungeon = self.dm_session.find(DUNGEON, bound_dungeon)
                if not (
                    (permitions := dungeon.get_user(user_id=self.current_client_data["user_id"]).permitions).get("edit_room") == room_id or
                    permitions.get("edit_rooms")
                ):
                    raise ErrorMessage("Not authorized")
                room = dungeon.new_room(room_id=room_id)
            else:
                if not room.dungeon_id == bound_dungeon:
                    raise ErrorMessage("Wrong dungeon bound.")
                try:
                    dungeon = self.dm_session.find(DUNGEON, bound_dungeon)
                except KeyError:
                    raise ErrorMessage("Dungeon does not exist.")
                if not (
                    (permitions := dungeon.get_user(user_id=self.current_client_data["user_id"]).permitions).get("edit_room") == room_id or
                    permitions.get("edit_rooms")
                ):
                    raise ErrorMessage("Not authorized")
            room.content = content
            room.write()
            dungeon.log_update()
            dungeon.write()
            return "Success!"
        
        @self.request_handler.request(name="load_room", allow_python_syntax=True, auto_convert=True)
        def load_room(room_id : RoomId) -> str:
            room : Room
            room = self.dm_session.find(ROOM, room_id)
            return room.content
        
        @self.request_handler.request(name="like_dungeon")
        def like_dungeon(dungeon_id : DungeonId):
            dungeon : Dungeon
            user : User
            self.ensure_login()
            dungeon = self.dm_session.find(DUNGEON, dungeon_id)
            user = self.find_current_client_user()
            dungeon.like(user)
            return "Success!"
        
        @self.request_handler.request(name="unlike_dungeon")
        def unlike_dungeon(dungeon_id : DungeonId):
            dungeon : Dungeon
            user : User
            self.ensure_login()
            dungeon = self.dm_session.find(DUNGEON, dungeon_id)
            user = self.find_current_client_user()
            dungeon.unlike(user)
            return "Success!"
        
        self.request_handler.start(thread=thread, duration=duration)
        
    def stop(self):
        """
        Stop the dungeon maker backend.
        """
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
        
    def ensure_login(self) -> None:
        """
        Ensure the user is logged in.
        """
        if not self.current_client_data.get("logged_in", False):
            raise ErrorMessage("You are not logged in")
        
    
    def find_current_client_user(self) -> User:
        """
        Find the User Account associated with the current user.
        """
        self.ensure_login()
        return self.dm_session.find(USER, self.current_client_data["user_id"])





def gen_passdata(*, username : str, password : str) -> bytes:
    """
    Generate passdata for an account
    """
    passdata = sha3_256(pickle.dumps((username, password, "Dungeon Maker: Reinvented - Login System Salt"))).digest()
    return passdata

def find_comment(project : Project, *, content : str = None, user : str = None) -> bool:
    """
    Find a comment.
    """
    comments = project.comments()
    for comment in comments:
        if user and comment["author"]["username"] != user:
            continue
        if content and comment["content"] != content:
            continue
        return True
    return False

def user_has_linked(*, session : DMSession, user : str) -> Union[None, dict]:
    """
    Find out if a user has linked an account to his name.
    """
    try:
        has_linked = session.database_abstraction.select_user(fields={"linked_user": user})
    except KeyError:
        return None
    else:
        return has_linked

def include_data(data : dict, *, include : list[str] = ()) -> dict:
    """
    Remove all elements from a dict except those specified
    """
    new = {}
    for i in include:
        new[i] = data.get(i)
    return new

















