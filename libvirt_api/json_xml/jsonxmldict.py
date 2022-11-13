from __future__ import annotations

import random

from libvirt_api.json_xml import *


class JsonXmlDict(dict):
    """
    this class creates a task object that can be mapped to xml or json
    """
    # this is used in the json requests to write the task to be executed
    COMMAND_JSON_FIELD = 'libvirt_command'
    # arguments for the command / function (kwargs or 'keyword args' are included here too)
    ARGS_JSON_FIELD = 'libvirt_args'

    def get_or_error(self, attribute, context, null_value=-1):
        # TODO: 🔴🔴🔴 add context to all occurrences of this function
        result = self.get(attribute, null_value)
        if result == null_value:
            # the value of the attribute might actually be equal to -1, so make sure the attribute really doesn't exist
            if attribute not in self.keys():
                raise AttributeError(f"attribute '{attribute}' not found, context : {context}")
        return result

    def __init__(self, dict_or_json_str):
        # init self with data from json
        if isinstance(dict_or_json_str, str):
            super().__init__(json_to_dict(dict_or_json_str))
        elif isinstance(dict_or_json_str, dict):
            super(JsonXmlDict, self).__init__(dict_or_json_str)

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
        return self.get(JsonXmlDict.COMMAND_JSON_FIELD)

    @property
    def args(self) -> JsonXmlDict:
        """
        :return: returns the arguments included in the dict, an empty dict
        """
        res = self.get(JsonXmlDict.ARGS_JSON_FIELD, dict())
        return JsonXmlDict(res)
