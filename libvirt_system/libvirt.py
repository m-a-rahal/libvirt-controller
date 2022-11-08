import threading
import multiprocessing
from json_xml import *


# libvirt
class LibvirtManager:
    COMMAND_JSON_FIELD = 'libvirt_command'  # this is used in the json requests to write the task to be executed
    ARGS_JSON_FIELD = 'libvirt_args'        # arguments for the command / function (kwargs or 'keyword args' are included here too)

    def __int__(self, default_connection_uri = 'qemu:///system'):
        self.Q = multiprocessing.SimpleQueue
        self.default_connection_uri = default_connection_uri
        self.conn = self.create_connection_to_libvrit(default_connection_uri)

    @staticmethod
    def alert(self, source, message):
        """
        alerts the NAT with a message
        """

    # libvrirt worker thread
    def libvirt_worker(self, source, task : str, task_id=''):
        # TODO: complete conception here
        """
        :param source: the source, the sender of the task ~ (not yet defined)
        :param task: json string of the task, retrieved from queue
        :param task_id: ID of the task ~ (not yet defined)
        :return: nothing
        """
        # alert NAT
        self.alert(source, f"task {task_id} is being processed ...")
        self.do_task(task)
        # alert NAT
        self.alert(source, f"task {task_id} is done.")

    # this maps all libvirt API methods to tasks
    def do_task(self, task : str):
        """
        executes json task
        :param task: json string encoding the task to be done
        :return:
        """
        task_dict = json_to_dict(task)
        command = task_dict.get(LibvirtManager.COMMAND_JSON_FIELD)  # get the command
        arguments = task_dict.get(LibvirtManager.ARGS_JSON_FIELD)   # get command args/kwargs
        if command == 'open_connection':
            # you may choose to create a new connection for some reason
            # you must have the name of the connection saved to pass it over for other commands
            # TODO: create this if needed
            pass
        elif command == 'createXML':
