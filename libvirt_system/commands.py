from __future__ import annotations
from enum import Enum, auto
from libvirt_system.task import Task
from libvirt import virDomain, virConnect
from libvirt_system.exceptions import print_stderr
from libvirt_system.domain import Domain

commands = dict()


class Command(Enum):
    open_connection = auto()
    # domain (VM) state change
    defineXML = auto()  # define + RUN domain
    createXML = auto()  # define domain
    domain_suspend = auto()  # suspend domain
    domain_resume = auto()  # resume domain
    domain_save = auto()  # save domain
    domain_restore = auto()  # restore saved domain
    domain_start = auto()  # start a defined domain
    domain_shutdown = auto()  # shutdown domain # TODO: 🟡 are there other state changes ?

    @classmethod
    def parse(cls, command_str) -> Command or None:
        """returns enum for provided command string, or None"""
        return cls._member_map_.get(command_str, None)


def open_connection(task: Task):
    # you may choose to create a new connection for some reason
    # you must have the name of the connection saved to pass it over for other commands
    # TODO: 🟢 create this if needed
    pass


# TODO: this part might need to be redone
def createXML(connection: virConnect, task: Task):
    # createXMl command must have and argument called 'xml' that contains the json equivalent of the xml file
    arguments = task.args
    xml = arguments['xml']  # TODO: make sure this is right
    domain = connection.createXML(xml)
    if domain is None:
        print_stderr(f'failed to create domain from XML definition')  # TODO: maybe be more descriptive here
    else:
        print_stderr(f'Guest {domain.name()} has booted.', raise_exception=False)
    return domain


def defineXML(connection: virConnect, task: Task):
    arguments = task.args
    domain = connection.defineXML(arguments['xml'])
    if domain is None:
        print_stderr(f'failed to define domain from XML definition')
    else:
        print_stderr(f'Guest {domain.name()} successfully defined.', raise_exception=False)
        # cast domain (virDomain) to Domain class (to have extra functionality)
        domain = Domain.cast(domain)
        return domain.get_state()  # TODO: 🔴 what to do here, what to return?


def domain_suspend(connection: virConnect, task: Task):
    domain = Domain.lookup_domain(connection, task)
    domain.suspend()
    return domain.get_state()  # TODO: 🔴 what to do here, what to return?
