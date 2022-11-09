from __future__ import annotations
from enum import Enum, auto
from libvirt_system.task import Task
from libvirt import virDomain, virConnect
from libvirt_system.exceptions import print_stderr
from libvirt_system.domain import Domain
import libvirt

commands = dict()


# NOTE: 🟩 means implemented, 🔗 means linked to 'switch-case' statements
# TODO: 🔴[📨response] These command's return won't be use, so instead send responses with 'position: "final"'
# TODO: 🔴[📨response] each response must identify the destination, so include that somewhere somehow
class Command(Enum):
    # lookups
    lookupByName = auto()  # 🟩🔗
    lookupByID = auto()  # 🟩🔗
    lookupByUUIDString = auto()  # 🟩🔗
    lookupByUUID = auto()  # 🟩🔗
    # connection
    open_connection = auto()  # 🟩🔗
    # domain get state
    domain_get_state = auto()  # 🟩🔗
    # domain (VM) state change, TODO: 🔴[📨response] all these must respond with new domain info (or error)
    defineXML = auto()  # 🟩🔗 define + RUN domain
    createXML = auto()  # 🟩🔗 define domain
    domain_suspend = auto()  # 🟩🔗 suspend domain
    domain_resume = auto()  # 🟩🔗 resume domain
    domain_save = auto()  # 🟩🔗 save domain
    domain_restore = auto()  # 🟩🔗restore saved domain
    domain_create = auto()  # 🟩🔗 start a defined domain
    domain_shutdown = auto()  # 🟩🔗 shutdown domain
    domain_destroy = auto()  # 🟩🔗 destroy domain

    # TODO: 🟡 are there other state changes ?

    @classmethod
    def parse(cls, command_str) -> Command or None:
        """returns enum for provided command string, or None"""
        return cls._member_map_.get(command_str, None)


def lookupByName(connection: virConnect, task: Task):
    x = task.get_or_error('name', context=f'lookupByName(name)')
    domain = connection.lookupByName(x)
    if domain is None:
        print_stderr(f"domain name={x} does not exist, or lookup failed")
    return domain


def lookupByID(connection: virConnect, task: Task):
    x = task.get_or_error(id, context=f'lookupByID(id)')
    domain = connection.lookupByID(x)
    if domain is None:
        print_stderr(f"domain id={x} does not exist, or lookup failed")
    return domain


def lookupByUUID(connection: virConnect, task: Task):
    attribute = 'uuid'
    x = task.get_or_error('uuid', context=f'lookupByUUID(uuid)')
    domain = connection.lookupByUUID(x)
    if domain is None:
        print_stderr(f"domain uuid={x} does not exist, or lookup failed")
    return domain


def lookupByUUIDString(connection: virConnect, task: Task):
    x = task.get_or_error('uuidstr', context=f'lookupByUUIDString(uuidstr)')
    domain = connection.lookupByUUIDString(x)
    if domain is None:
        print_stderr(f"domain uuidstr={x} does not exist, or lookup failed")
    return domain


def domain_destroy(connection: virConnect, task: Task):
    domain = Domain.lookup_domain(connection, task)
    domain.destroy()
    return domain.get_state().name


def domain_shutdown(connection: virConnect, task: Task):
    domain = Domain.lookup_domain(connection, task)
    domain.shutdown()
    return domain.get_state().name


def domain_create(connection: virConnect, task: Task):
    domain = Domain.lookup_domain(connection, task)
    domain.create()
    return domain.get_state().name


def domain_restore(connection: virConnect, task: Task):
    frm = task.get_or_error('frm', context='domain_restore(frm)')  # restore from file
    domain = connection.restore(frm)
    return domain  # TODO: 🔴💥 what does 'restore' return? check result, if None etc.


def domain_save(connection: virConnect, task: Task):
    domain = Domain.lookup_domain(connection, task)
    to = task.get_or_error('to', context='domain_save(to)')
    domain.save(to)
    return domain.get_state().name  # state should not be running


def domain_resume(connection: virConnect, task: Task):
    domain = Domain.lookup_domain(connection, task)
    domain.resume()
    return domain.get_state().name


def domain_get_state(connection: virConnect, task: Task) -> str:
    domain = Domain.lookup_domain(connection, task)
    return domain.get_state().name


def domain_suspend(connection: virConnect, task: Task):
    domain = Domain.lookup_domain(connection, task)
    domain.suspend()
    return domain.get_state().name  # TODO: 🔴 return state?


def open_connection(task: Task):
    # TODO: 🟢 create this if needed
    name = task.get_or_error('name', context='open_connection(name) / libvirt.open(name) / name ~ uri, eg: name = '
                                             '"qemu:///system"')
    connection = libvirt.open(name)
    if connection is None:
        print_stderr(f'Failed to open connection name={name}')
    print_stderr(f'Connection name={name} successful', raise_exception=False)
    return connection


def createXML(connection: virConnect, task: Task) -> Domain:
    """
    calls libvirt.createXML(xmlDesc, flags)
    :param task: fields: xmlDesc (required), flags (not required)
    :return: returns created domain object
    """
    # createXMl command must have and argument called 'xml' that contains the json equivalent of the xml file
    arguments = task.args
    xml = arguments.get_or_error('xmlDesc', context='createXML(xmlDesc,[flags])')  # required
    flags = arguments.get('flags', 0)  # not required
    domain = connection.createXML(xml, flags)
    if domain is None:
        print_stderr(f'failed to create domain from XML definition')  # TODO: maybe be more descriptive here
    else:
        print_stderr(f'Guest {domain.name()} has booted.', raise_exception=False)
    return Domain.cast(domain)


def defineXML(connection: virConnect, task: Task) -> Domain:
    arguments = task.args
    domain = connection.defineXML(arguments.get_or_error('xml', context='defineXML(xml)'))
    if domain is None:
        print_stderr(f'failed to define domain from XML definition')
    else:
        print_stderr(f'Guest {domain.name()} successfully defined.', raise_exception=False)
    # cast domain (virDomain) to Domain class (to have extra functionality)
    return Domain.cast(domain)
