import random
import threading
import multiprocessing
import libvirt
import sys
from json_xml import *
from libvirt_system.domain import Domain
from libvirt_system.exceptions import print_stderr
from libvirt_system.task import Task, JsonDict
from libvirt_system.commands import *


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
        command = Command.parse(task.command)  # get the command
        arguments = task.args  # get command args/kwargs
        # ease of use
        connection = self.connection
        # lookups
        if command == Command.lookupByName:
            lookupByName(connection, task)
        if command == Command.lookupByID:
            lookupByID(connection, task)
        if command == Command.lookupByUUID:
            lookupByUUID(connection, task)
        if command == Command.lookupByUUIDString:
            lookupByUUIDString(connection, task)
        # open connection
        if command == Command.open_connection:
            open_connection(task)
        # domain state change commands
        elif command == Command.createXML:
            createXML(connection, task)
        elif command == Command.defineXML:
            defineXML(connection, task)
        elif command == Command.domain_suspend:
            domain_suspend(connection, task)
        elif command == Command.domain_resume:
            domain_resume(connection, task)
        elif command == Command.domain_save:
            domain_save(connection, task)
        elif command == Command.domain_restore:
            domain_restore(connection, task)
        elif command == Command.domain_get_state:
            domain_get_state(connection, task)
        elif command == Command.domain_create:
            domain_create(connection, task)
        elif command == Command.domain_shutdown:
            domain_shutdown(connection, task)
        elif command == Command.domain_destroy:
            domain_destroy(connection, task)

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
            return None
        print_stderr(f'Connection name={uri} successful', raise_exception=False)
        return connection