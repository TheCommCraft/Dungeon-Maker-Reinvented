"""
Submodule for handling incoming requests.
"""
import re, warnings, ast
from func_timeout import StoppableThread
from typing import Union
from types import FunctionType
from scratchcommunication.cloud_socket import CloudSocketConnection
from .basetypes import BaseRequestHandler

class RequestHandler(BaseRequestHandler):
    """
    Class for request handlers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = self.cloud_socket.cloud.project_id
        self.requests = {}
        self.thread = None
        self.current_client = None
        self.current_client_username = None
        
    def request(self, func : FunctionType = None, *, name : str = None, auto_convert : bool = True, allow_python_syntax : bool = True, thread : bool = False) -> Union[FunctionType, None]:
        """
        Decorator for adding requests.
        """
        if func:
            func.__name__ = name or func.__name__
            func.auto_convert = auto_convert
            func.allow_python_syntax = allow_python_syntax
            func.thread = thread
            self.requests[func.__name__] = func
            return
        return lambda x : self.request(x, name=name, auto_convert=auto_convert, allow_python_syntax=allow_python_syntax)
    
    def add_request(self, func : FunctionType, *, name : str = None, auto_convert : bool = True, allow_python_syntax : bool = True, thread : bool = False):
        """
        Method for adding requests.
        """
        func.__name__ = name or func.__name__
        func.auto_convert = auto_convert
        func.allow_python_syntax = allow_python_syntax
        func.thread = thread
        self.requests[func.__name__] = func
    
    def start(self, *, thread : bool = None):
        """
        Method for starting the request handler.
        """
        self.cloud_socket.listen()
        if thread or (thread is None and self.uses_thread):
            self.thread = StoppableThread(target=lambda : self.start(thread=False))
            self.thread.start()
            return
        clients : list[tuple[CloudSocketConnection, str]] = []
        while True:
            try:
                clients.append(self.cloud_socket.accept(timeout=0))
            except TimeoutError:
                pass
            for client, username in clients:
                try:
                    msg = client.recv(timeout=0)
                except TimeoutError:
                    pass
                else:
                    response = "No response."
                    try:
                        self.current_client = client
                        self.current_client_username = username
                        raw_sub_requests = [raw_request.strip() for raw_request in msg.split(";")]
                        sub_request_names = [re.match(r"\w+", raw_request).group() for raw_request in raw_sub_requests]
                        for req_name, raw_req in zip(sub_request_names, raw_sub_requests):
                            if re.match(r"\w+\(.*\)$", raw_req) and self.requests[req_name].allow_python_syntax:
                                name, args, kwargs = parse_python_request(raw_req, req_name)
                            elif not re.match(r"\w+(.*)$", raw_req):
                                name, args, kwargs = parse_normal_request(raw_req, req_name)
                            else:
                                raise PermissionError("Python syntax is not allowed for this.")
                            response = self.execute_request(name, args, kwargs)
                    except Exception:
                        response = "There was an error."
                        warnings.warn("Received a request with an invalid syntax.", SyntaxWarning)
                    client.send(str(response))
    
    def execute_request(self, name, args, kwargs) -> Union[str, float, int]:
        return self.requests[name](*args, **kwargs)
                    

def parse_python_request(msg, name):
    parsed = ast.parse(msg).body[0].value
    assert parsed.func.id == name
    name = parsed.func.id
    args = [arg.value for arg in parsed.args]
    kwargs = {kwarg.arg: kwarg.value.value for kwarg in parsed.keywords}
    return name, args, kwargs

def parse_normal_request(msg, name):
    i = iter(msg)
    STR = "str"
    NUM = "num"
    FLT = "float"
    ID = "id"
    MT = "space"
    mode = ID
    content = ""
    args = []
    while True:
        try:
            n = next(i)
            if mode == ID:
                if n == " ":
                    mode = MT
                    args.append(content)
                    content = ""
                    n = next(i)
                else:
                    content += n
            if mode == MT:
                if n in '\'"':
                    open_type = n
                    mode = STR
                    n = next(i)
                elif n.isnumeric() or n == ".":
                    mode = NUM
                else:
                    raise SyntaxError(n)
            if mode == FLT:
                if n == " ":
                    mode = MT
                    args.append(float(content))
                    content = ""
                    continue
                content += n
            if mode == NUM:
                if n == " ":
                    mode = MT
                    args.append(int(content))
                    content = ""
                    continue
                if n == ".":
                    mode = FLT
                content += n
            if mode == STR:
                if n == open_type:
                    n = next(i)
                    assert n == " "
                    mode = MT
                    args.append(content)
                    content = ""
                    continue
                if n == "\\":
                    n = next(i)
                content += n
        except StopIteration:
            args.append(float(content) if mode == FLT else (int(content) if mode == NUM else content))
            break
    assert args.pop(0) == name
    return name, args, {}





















