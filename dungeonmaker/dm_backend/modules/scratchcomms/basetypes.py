"""
Submodule for base types
"""
from threading import Thread
from typing import Mapping, Union
from types import FunctionType
from dataclasses import dataclass, field
from scratchcommunication.cloud_socket import CloudSocket, CloudSocketConnection

@dataclass(slots=True)
class BaseRequestHandler:
    """
    Base class for request handlers.
    """
    project_id : int = field(init=False)
    cloud_socket : CloudSocket = field(kw_only=True)
    requests : Mapping[str, FunctionType] = field(init=False)
    uses_thread : bool = field(kw_only=True, default=False)
    thread : Union[Thread, None] = field(init=False)
    current_client : Union[CloudSocketConnection, None] = field(init=False)
    current_client_username : Union[str, None] = field(init=False)






















