import threading
from dataclasses import dataclass
from typing import Any


@dataclass
class Future:
    """use this to receive future value returned by a thread (not a process)"""
    return_value: Any = None


def run_as_thread(thread_list: list = None):
    """run the specified function as thread and add it to thread list (to wait for them later)
    the function must have a field to accept return type"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            t = threading.Thread(target=f, args=args, kwargs=kwargs)
            t.start()
            if thread_list is not None:
                thread_list.append(t)
            return t
        return wrapper
    return decorator

