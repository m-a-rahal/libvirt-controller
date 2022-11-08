import random
from json_xml import *


class Task(dict):
    """
    this class creates a task object that can be mapped to xml or json
    """
    # this is used in the json requests to write the task to be executed
    COMMAND_JSON_FIELD = 'libvirt_command'
    # arguments for the command / function (kwargs or 'keyword args' are included here too)
    ARGS_JSON_FIELD = 'libvirt_args'

    def __init__(self, task_json):
        # init self with data from json
        super().__init__(json_to_dict(task_json))

    @property
    def json(self):
        return dict_to_json(self)

    @property
    def xml(self):
        return dict_to_xml(self)

    @property
    def source(self):
        # TODO: 🟠 implement this properly or delete it
        return self.get('source', 'unknown_source')

    @property
    def task_id(self):
        # TODO: 🟠 implement this or delete it
        return self.get('task_id', random.randint(0, 10000))

    @property
    def command(self):
        return self.get(Task.COMMAND_JSON_FIELD)

    def args(self):
        return self.get(Task.ARGS_JSON_FIELD)
