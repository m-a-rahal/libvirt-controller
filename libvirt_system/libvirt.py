import random
import threading
import multiprocessing
import libvirt
import sys
from json_xml import *
from libvirt_system.io import print_stderr
from libvirt_system.task import Task


class LibvirtManager:

    def __init__(self, default_connection_uri='qemu:///system'):
        self.q = multiprocessing.SimpleQueue
        self.q_lock = multiprocessing.Lock()  # lock for synchronizing q
        self.default_connection_uri = default_connection_uri
        self.conn = self.create_connection_to_libvirt(default_connection_uri)
        if self.conn is None:
            exit(1)  # failed to make connection

    def alert(self, source, message):
        """
        alerts the NAT with a message
        """
        pass  # TODO: 🔴 define this method

    # libvrirt worker thread
    def libvirt_worker(self, task: str):
        # TODO: complete conception here
        """
        :param source: the source, the sender of the task ~ (not yet defined)
        :param task: json string of the task, retrieved from queue
        :param task_id: ID of the task ~ (not yet defined)
        :return: nothing
        """
        # alert NAT
        task = Task(task)  # transform json into Task object
        self.alert(task.source, f"task {task.task_id} is being processed ...")
        self.do_task(task)
        # alert NAT
        self.alert(task.source, f"task {task.task_id} is done.")
        # 🟢 check if there aren't any other tasks on the Queue
        q = self.q
        task = None
        with self.q_lock:
            if not q.empty():
                task = q.get()
        if task is not None:
            self.libvirt_worker(task)

    # this maps all libvirt API methods to tasks
    def do_task(self, task: Task):
        """
        executes json task
        :param task: json string encoding the task to be done
        :return: ###
        """
        command = task.command  # get the command
        arguments = task.args  # get command args/kwargs
        # ease of use
        conn = self.conn
        if command == 'open_connection':
            # you may choose to create a new connection for some reason
            # you must have the name of the connection saved to pass it over for other commands
            # TODO: create this if needed
            pass
        elif command == 'createXML':  # TODO: this part might need to be redone
            # createXMl command must have and argument called 'xml' that contains the json equivalent of the xml file
            xml = arguments['xml']  # TODO: make sure this is right
            domain = conn.createXML(xml)
            if domain is None:
                print_stderr(f'failed to create domain from XML definition')  # TODO: maybe be more descriptive here
            else:
                print_stderr(f'Guest {domain.name()} has booted.')
            return domain

        elif command == 'defineXML':
            domain = conn.defineXML(arguments['xml'])
            if domain is None:
                print_stderr(f'failed to define domain from XML definition')
            else:
                print_stderr(f'')

        elif command == '':
            pass

    @staticmethod
    def create_connection_to_libvirt(uri):
        """
        Establishes connection and returns None if there's nothing to return
        :param uri: connection
        :return:
        """
        conn = libvirt.open(uri)
        if conn is None:
            print_stderr(f'Failed to open connection to {uri}')
            return None
        print_stderr('Connection successful')
        return conn
