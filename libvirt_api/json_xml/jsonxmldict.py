from __future__ import annotations
import random
from enum import Enum
from libvirt_api.exceptions import JsonXMlError
from libvirt_api.json_xml import *


class DataType:
    xml = 0
    json = 1


# ========================================================================================================
# json/xml commands and data =============================================================================
# ========================================================================================================

class CommandSyntax(Enum):
    command = 'command'
    args = 'args'

class JsonXmlDict(dict):
    """
    this class creates a task object that can be mapped to xml or json
    """
    # this is used in the json requests to write the task to be executed
    COMMAND_SYNTAX = CommandSyntax.command
    # arguments for the command / function (kwargs or 'keyword args' are included here too)
    ARGS_JSON_FIELD = CommandSyntax.args

    def __init__(self, data, data_type: DataType = DataType.json):  # json by default
        # init self with data from json
        if isinstance(data, str):
            if data_type == DataType.json:
                super().__init__(json_to_dict(data))
            elif data_type == DataType.xml:
                super().__init__(xml_to_dict(data))
            else:
                raise JsonXMlError.UnknownDataType(f"{data_type} is not a valid data type")
        elif isinstance(data, dict):
            super(JsonXmlDict, self).__init__(data)

    def get_or_error(self, attribute, context, null_value=-1):
        # TODO: 🔴🔴🔴 add context to all occurrences of this function
        result = self.get(attribute, null_value)
        if result == null_value:
            # the value of the attribute might actually be equal to -1, so make sure the attribute really doesn't exist
            if attribute not in self.keys():
                raise JsonXMlError.AttributeNotFoundError(f"attribute '{attribute}' not found, context : {context}")
        return result

    @property
    def json(self):
        return dict_to_json(self)

    @property
    def xml(self):
        return dict_to_xml(self)

    @property
    def source(self):
        # the source, the sender of the task ~ (not yet defined)
        # TODO: 🟠 implement this properly or delete it
        return self.get('source', 'unknown_source')

    @property
    def task_id(self):
        # ID of the task ~ (not yet defined)
        # TODO: 🟠 implement this or delete it
        return self.get('task_id', random.randint(0, 10000))

    @property
    def command(self):
        return self.get(JsonXmlDict.COMMAND_SYNTAX)

    @property
    def args(self) -> JsonXmlDict:
        """
        :return: returns the arguments included in the dict, an empty dict
        """
        res = self.get(JsonXmlDict.ARGS_JSON_FIELD, dict())
        return JsonXmlDict(res)

    def get_by_path(self, path : str) -> tuple[dict | None | str, bool]:
        """
        retrieves the attribute specified by the path
        :param path: attribute names separated by /, eg: domain/os/type,   or /domain/@type
        :return: a couple (value, found), value= JsonDict representing the found attribute (or None if not found), found= if the attribute was found or not
        """
        path = PathXmlJson(path)
        attr = self
        # walk along path, one step at a time
        for i, name in enumerate(path[:-1]):  # treat all elements, except last one, treated separately
            try:
                value = attr.get_or_error(name, context=f"get_by_path({path} failed, {path.sub_path(i+1)} not found)")
            except JsonXMlError.AttributeNotFoundError:
                # path doesn't exist
                return None, False
            if isinstance(value, dict):
                attr = JsonXmlDict(value)
                continue
            else:
                # path found, but it's empty, must raise exception
                raise JsonXMlError.PathIsEmpty(path, path.sub_path(i + 1), value)

        # return last element of the path (if exists)
        try:
            value = attr.get_or_error(path[-1], context=f"get_by_path({path} failed, {path} not found)")
            if isinstance(value, dict):
                value = JsonXmlDict(value)
            else:
                assert isinstance(value, str)
            return value, True
        except JsonXMlError.AttributeNotFoundError:
            # path doesn't exist
            return None, False
class PathXmlJson(list):
    def __init__(self, path: str, separator: str = '/'):
        self._path = path
        self._sep = separator
        elements = path.strip().split(separator)
        super().__init__(elements)

    def sub_path(self, index: int):
        return self._sep.join(self[index])

    def __str__(self):
        return self._path
