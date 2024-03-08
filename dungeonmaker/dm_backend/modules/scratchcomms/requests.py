"""
Submodule for handling incoming requests.
"""
import re, warnings, ast, inspect
from func_timeout import StoppableThread
from typing import Union, Mapping, Sequence, Any
from types import FunctionType
from scratchcommunication.cloud_socket import CloudSocketConnection
from .basetypes import BaseRequestHandler, StopRequestHandler, NotUsingAThread

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
            self.uses_thread = True
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
                    continue
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
                        self.execute_request(name, args=args, kwargs=kwargs, client=client)
                        response = None
                except Exception:
                    response = "There was an error."
                    warnings.warn("Received a request with an invalid syntax.", SyntaxWarning)
                if response:
                    client.send(response)
                
    
    def execute_request(self, name, *, args : Sequence[Any], kwargs : Mapping[str, Any], client : CloudSocketConnection) -> Union[str, float, int]:
        """
        Execute a request.
        """
        request_handling_function = self.requests[name]
        return_converter = lambda x : x
        if request_handling_function.auto_convert:
            for idx, (arg, annotation) in enumerate(inspect.signature(request_handling_function).parameters.items()):
                if inspect.Parameter.empty == annotation.annotation:
                    continue
                if not arg in kwargs:
                    args[idx] = annotation.annotation(args[idx])
                    continue
                kwargs[arg] = annotation.annotation(kwargs[arg])
            if inspect.signature(request_handling_function).return_annotation:
                return_converter = inspect.signature(request_handling_function).return_annotation
        def respond():
            client.send(str(return_converter(request_handling_function(*args, **kwargs))))
        if request_handling_function.thread:
            thread = StoppableThread(target=respond)
            thread.start()
            return
        respond()
    
    def stop(self):
        """
        Stop the request handler
        """
        if self.uses_thread:
            raise NotUsingAThread("Can't stop a request handler that is not using a thread.")
        self.thread.stop(StopRequestHandler)
        self.cloud_socket.stop()
                    

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





















