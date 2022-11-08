import random
import threading
import multiprocessing
import libvirt
import sys
from json_xml import *
from libvirt_system.domain import Domain
from libvirt_system.exceptions import MissingAttributeError, UnrecognizedOption, print_stderr
from libvirt_system.task import Task, JsonDict


class LibvirtManager:
    def __init__(self, default_connection_uri='qemu:///system'):
        # task queue and workers
        self.queue = multiprocessing.SimpleQueue
        self.queue_lock = multiprocessing.Lock()  # lock for synchronizing q
        self.active_workers = multiprocessing.Value('i', 0)
        self.MAX_WORKERS = multiprocessing.Value('i', 4)  # Value('i', n) : 'i' means 'integer', and n is the value
        # main connection
        self.default_connection_uri = default_connection_uri
        self.connection = self.create_connection_to_libvirt(default_connection_uri)
        if self.connection is None:
            exit(1)  # failed to make connection

    @staticmethod
    def alert(source, message):
        """
        alerts the NAT with a message
        """
        pass  # TODO: 🔴 define this method

    # libvirt main process/thread
    def receive_task(self, task):
        # if number of workers exceeded, put task in queue
        # otherwise, create new process to handle task
        pass

    @staticmethod
    def libvirt_worker(task: str, queue, lock):
        # TODO: complete conception here
        # alert NAT
        task = Task(task)  # transform json into Task object
        LibvirtManager.alert(task.source, f"task {task.task_id} is being processed ...")
        # run the task
        LibvirtManager.do_task(task)
        # alert NAT
        LibvirtManager.alert(task.source, f"task {task.task_id} is done.")
        # 🟢 check if there aren't any other tasks on the Queue
        task = None
        with lock:
            if not queue.empty():
                task = queue.get()
        if task is not None:
            LibvirtManager.libvirt_worker(task, queue, lock)

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
        connection = self.connection
        if command == 'open_connection':
            # you may choose to create a new connection for some reason
            # you must have the name of the connection saved to pass it over for other commands
            # TODO: create this if needed
            pass
        elif command == 'createXML':  # TODO: this part might need to be redone
            # createXMl command must have and argument called 'xml' that contains the json equivalent of the xml file
            xml = arguments['xml']  # TODO: make sure this is right
            domain = connection.createXML(xml)
            if domain is None:
                print_stderr(f'failed to create domain from XML definition')  # TODO: maybe be more descriptive here
            else:
                print_stderr(f'Guest {domain.name()} has booted.')
            return domain

        elif command == 'defineXML':
            domain = connection.defineXML(arguments['xml'])
            if domain is None:
                print_stderr(f'failed to define domain from XML definition')
            else:
                print_stderr(f'')

        elif command == 'domain_suspend':
            domain = Domain.lookup_domain(self.connection, task)
            domain.get_info()
            domain.suspend()


    @staticmethod
    def create_connection_to_libvirt(uri):
        """
        Establishes connection and returns None if there's nothing to return
        :param uri: connection
        :return:
        """
        connection = libvirt.open(uri)
        if connection is None:
            print_stderr(f'Failed to open connection to {uri}')
            return None
        print_stderr('Connection successful')
        return connection

    def lookup_domain(self, task: Task) -> libvirt.virDomain:
        """
        lookup domain using ID, UUID or name,
        the lookup method must be specified in the task/request under 'lookup' field
        the identifier (name, id or UUID) must be present in the request as well:
        examples:
            task1 = {lookup : uuid, uuid : 156454-165454-....}
            task2 = {lookup : name, name : user156_VM2}
        :param task: a json like object of class Task
        :return: returns a virDomain object
        """
        connection = self.connection
        lookup = task.get_or_error('lookup').lower()
        if lookup == 'name':
            x = name = task.get_or_error('name')
            domain = connection.lookupByName(name)
        elif lookup == 'uuid':
            x = uuid = task.get_or_error('uuid')
            domain = connection.lookupByUUID(uuid)
        elif lookup == 'id':
            x = id_ = task.get_or_error('id')
            domain = connection.lookupByID(id_)
        # TODO: 🟡 maybe add UUIDString ?
        else:
            raise UnrecognizedOption(f'lookup = {lookup} is not a valid/implemented option')

        if domain is None:
            raise Exception(f"domain {lookup}={x} does not exist, or lookup failed")
        return domain
