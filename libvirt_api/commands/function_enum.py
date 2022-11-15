from __future__ import annotations

class FunctionEnum:
    """I tried creating enums with values = functions, but that didn't work
    So I created this class as a wrapper for those functions, and it works inside enums

    example:
    say you have functions:  f1, f2, f3 ...
    and you wanted to make this:
    class Commands(Enum):
        command1 = f1
        command2 = f2
        command3 = f3

    this causes weird behavior, try it.
    didn't work, instead wrap the functions with FunctionEnum:
    class Commands(Enum):
        command1 = FunctionEnum(f1)
        command2 = FunctionEnum(f2)
        command3 = FunctionEnum(f3)

    now our "commands" are well named, and callable like so:
    command_i.value(arguments...)       which is equivalent to: f_i(args...)
    """
    counter = 0

    def __init__(self, f: callable):
        self.value = FunctionEnum.counter = FunctionEnum.counter + 1
        self.f = f

    def __call__(self, *args, **kwargs):
        """this means calling a FunctionEnum calls it's inner function"""
        return self.f(*args, **kwargs)
