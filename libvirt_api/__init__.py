import multiprocessing

import libvirt_api.commands
from libvirt_api.commands import *
from libvirt_api.commands.bindings import Command
from libvirt_api.exceptions import Position, print_stderr
from libvirt_api.json_xml.jsonxmldict import JsonXmlDict


class LibvirtManager:
    def __init__(self, default_connection_uri='qemu:///system'):
        # main connection
        self.default_connection_uri = default_connection_uri

    # 🌟 use context manager ('with' statement)  to make sure connection is closed at the end -----------------------
    def __enter__(self, connection_uri: str or None = None):
        # create connection
        if not connection_uri:
            connection_uri = self.default_connection_uri
        self.connection = self.create_connection_to_libvirt(connection_uri)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
    # ----------------------------------------------------------------------------------------------------------

    # libvirt main process/thread
    def receive_task(self, task):
        # for now, will simply call (do_task)
        # TODO: properly implement task reception
        print_stderr('request received', pos='first', context=task, raise_exception=False)
        return self.do_task(task)

    # this maps all libvirt API methods to tasks
    def do_task(self, task: JsonXmlDict):
        """
        executes json task
        :param task: json string encoding the task to be done
        :return: ###
        """
        command = Command.parse(task.command)  # get the command
        if command is None:
            print_stderr(f'libvirt_command = "{command}" is not recognized!', pos=Position.last)
        arguments = task.args  # get command args/kwargs
        # ease of use
        connection = self.connection
        # run command
        command.value(connection, task)

    @staticmethod
    def create_connection_to_libvirt(uri):
        """
        Establishes connection and returns None if there's nothing to return
        :param uri: connection
        :return: connection object
        """
        connection = libvirt.open(uri)
        if connection is None:
            print_stderr(f'Failed to open connection to {uri}')
        print_stderr(f'Connection name={uri} successful', raise_exception=False)
        return connection
