from __future__ import annotations
import sys
from enum import Enum


class Position(Enum):
    first = 0
    middle = 1
    last = 3


def print_info(msg, pos: Position = Position.middle, context=None):
    # TODO: 🌊 always keep this up to date with 'print_stderr'
    return print_stderr(msg, raise_exception=False, pos=pos, context=context)


def print_stderr(msg, raise_exception=True, pos: Position = Position.middle, context=None):
    # TODO: 🔴 implement messaging ! add context, type, position and maybe other structural information like {domain:
    #  {uuid: 64546468-154648-154687-1546877}}
    print(msg, file=sys.stderr)
    if raise_exception:
        raise Exception(msg)

class JsonXMlError(Exception):

    class UnknownDataType(Exception):
        pass

    class AttributeNotFoundError(Exception):
        pass

    class PathIsEmpty(Exception):
        def __init__(self, path, sub_path, value):
            self.path = path
            self.sub_path = sub_path
            self.value = value
            super(JsonXMlError.PathIsEmpty, self).__init__(f"path {path} is invalid because {sub_path} is not a path (it's a final attribute with value = {value})")


class CantCreateDomainError(Exception):
    pass
