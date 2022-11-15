from __future__ import annotations
from enum import Enum
from libvirt_api.exceptions import JsonXMlError
from libvirt_api.json_xml import *


class DataType:
    xml = 0
    json = 1


# ========================================================================================================
# json/xml test_commands and data =============================================================================
# ========================================================================================================

class CommandSyntax(Enum):
    """the syntax used in JSON requests, example of a request :
    {
        'command' : 'domain_suspend'  #  command = suspend domain
        'args' : {
            'uuid' : '4dea22b3-1d52-d8f3-2516-782e98ab3fa0',    # this is the uuid of the domain to suspend
        }
    }"""
    # this is used in the json requests to write the task to be executed
    command = 'command'
    # arguments for the command / function (kwargs or 'keyword args' are included here too)
    args = 'args'


class JsonXmlDict(dict):
    """
    this class creates a task object that can be mapped to xml or json
    """

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

    def get_or_error(self, attribute, context: str):
        """
        NOTE: this method is optional, it's almost equivalent to dit[key]
        This method is attempts to find a given attribute in the dictionary (a key)
        if it's not found, it simply raises an error
        :param attribute: the attribute you're looking for in the dict
        :param context: if error, provide a message describing the error (the context of the error)
        :return:
        """
        try:
            return self[attribute]
        except KeyError:
            raise JsonXMlError.AttributeNotFoundError(f"attribute '{attribute}' not found, context : {context}")

    @property
    def json(self):
        return dict_to_json(self)

    @property
    def xml(self):
        return dict_to_xml(self)

    @property
    def command(self):
        """returns the command field in this dictionary"""
        return self[CommandSyntax.command.value]

    @property
    def args(self) -> JsonXmlDict:
        """returns the arguments field in this dictionary, or {} if no arguments are present"""
        res = self.get(CommandSyntax.args.value, dict())
        return JsonXmlDict(res)

    def get_by_path(self, path: str) -> tuple[dict | None | str, bool]:
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
                value = attr.get_or_error(name, context=f"get_by_path({path} failed, {path.sub_path(i + 1)} not found)")
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
