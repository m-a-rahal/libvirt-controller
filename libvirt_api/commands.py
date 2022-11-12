from __future__ import annotations
from enum import Enum, auto
import libvirt
from libvirt import virDomain, virConnect

from libvirt_api.domain import get_state
from libvirt_api.exceptions import print_stderr, print_info, Position
from libvirt_api.json_xml.jsonxmldict import JsonXmlDict


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


def lookupByName(connection: virConnect, task: JsonXmlDict):
    x = task.args.get_or_error('name', context=f'lookupByName(name)')
    domain = connection.lookupByName(x)
    if domain is None:
        print_stderr(f"domain name={x} does not exist, or lookup failed")
    return domain


def lookupByID(connection: virConnect, task: JsonXmlDict):
    x = task.args.get_or_error(id, context=f'lookupByID(id)')
    domain = connection.lookupByID(x)
    if domain is None:
        print_stderr(f"domain id={x} does not exist, or lookup failed")
    return domain


def lookupByUUID(connection: virConnect, task: JsonXmlDict):
    x = task.args.get_or_error('uuid', context=f'lookupByUUID(uuid)')
    domain = connection.lookupByUUID(x)
    if domain is None:
        print_stderr(f"domain uuid={x} does not exist, or lookup failed")
    return domain


def lookupByUUIDString(connection: virConnect, task: JsonXmlDict):
    x = task.args.get_or_error('uuidstr', context=f'lookupByUUIDString(uuidstr)')
    domain = connection.lookupByUUIDString(x)
    if domain is None:
        print_stderr(f"domain uuidstr={x} does not exist, or lookup failed")
    return domain


def get_new_state(domain: virDomain, connection: virConnect, task: JsonXmlDict):
    state = None
    try:
        state = get_state(domain).name
    except Exception as e:
        print_stderr('failed to get state', pos=Position.last)
    print_info(f'new state = {state}', pos=Position.last)
    return state


def domain_destroy(connection: virConnect, task: JsonXmlDict):
    domain = lookup_domain(connection, task)
    domain.destroy()
    return get_new_state(domain, connection, task)


def domain_shutdown(connection: virConnect, task: JsonXmlDict):
    domain = lookup_domain(connection, task)
    domain.shutdown()
    return get_new_state(domain, connection, task)

def domain_create(connection: virConnect, task: JsonXmlDict):
    domain = lookup_domain(connection, task)
    domain.create()
    return get_new_state(domain, connection, task)


def domain_restore(connection: virConnect, task: JsonXmlDict):
    frm = task.args.get_or_error('frm', context='domain_restore(frm)')  # restore from file
    domain = connection.restore(frm)
    return get_new_state(domain, connection, task)  # TODO: 🔴💥 what does 'restore' return? check result, if None etc.


def domain_save(connection: virConnect, task: JsonXmlDict):
    domain = lookup_domain(connection, task)
    to = task.args.get_or_error('to', context='domain_save(to)')
    domain.save(to)
    try:
        return get_new_state(domain, connection, task)
    except libvirt.libvirtError as e:
        if 'Domain not found' in e.get_error_message():
            # this means save is successful
            # TODO: 🟠 fine tune this error, does this look reasonable?
            print_info('domain saved successfuly', pos=Position.last)
        else:
            raise e


def domain_resume(connection: virConnect, task: JsonXmlDict):
    domain = lookup_domain(connection, task)
    domain.resume()
    return get_new_state(domain, connection, task)


def domain_get_state(connection: virConnect, task: JsonXmlDict) -> str:
    domain = lookup_domain(connection, task)
    return get_state(domain).name


def domain_suspend(connection: virConnect, task: JsonXmlDict):
    domain = lookup_domain(connection, task)
    domain.suspend()
    return get_new_state(domain, connection, task)

def open_connection(task: JsonXmlDict):
    # TODO: 🟢 create this if needed
    name = task.args.get_or_error('name', context='open_connection(name) / libvirt.open(name) / name ~ uri, eg: name = '
                                                  '"qemu:///system"')
    connection = libvirt.open(name)
    if connection is None:
        print_stderr(f'Failed to open connection name={name}')
    print_stderr(f'Connection name={name} successful', raise_exception=False)
    return connection


def createXML(connection: virConnect, task: JsonXmlDict) -> virDomain:
    """
    calls libvirt.createXML(xmlDesc, flags)
    :param task: fields: xmlDesc (required), flags (not required)
    :return: returns created domain object
    """
    # createXMl command must have and argument called 'xml' that contains the json equivalent of the xml file
    args = task.args
    xml = args.get_or_error('xmlDesc', context='createXML(xmlDesc,[flags])')  # required
    flags = args.get('flags', 0)  # not required
    print_info(f'creating domain ...')
    domain = connection.createXML(xml, flags)
    if domain is None:
        print_stderr(f'failed to create domain from XML definition')  # TODO: maybe be more descriptive here
    else:
        print_stderr(f'Guest {domain.name()} has booted.', raise_exception=False)
    return get_new_state(domain, connection, task)


def defineXML(connection: virConnect, task: JsonXmlDict) -> virDomain:
    args = task.args
    domain = connection.defineXML(args.get_or_error('xml', context='defineXML(xml)'))
    if domain is None:
        print_stderr(f'failed to define domain from XML definition')
    else:
        print_stderr(f'Guest {domain.name()} successfully defined.', raise_exception=False)
    # cast domain (virDomain) to Domain class (to have extra functionality)
    return get_new_state(domain, connection, task)


def lookup_domain(connection: libvirt.virConnect, task: JsonXmlDict, silent=False) -> virDomain:
    """
    lookup domain using ID, UUID or name,
    the lookup method must be specified in the task/request under 'lookup' field
    the identifier (name, id or UUID) must be present in the request as well:
    examples:
        task1 = {lookup : uuid, uuid : 156454-165454-....}
        task2 = {lookup : name, name : user156_VM2}
    :param connection: libvirt connection
    :param task: a json like object of class Task
    :return: returns a virDomain object
    """
    args = task.args
    domain: virDomain or None = None
    if 'id' in args:
        domain = lookupByID(connection, task)
    elif 'uuid' in args:
        domain = lookupByUUID(connection, task)
    elif 'uuidstr' in args:
        domain = lookupByUUIDString(connection, task)
    elif 'name' in args:
        domain = lookupByName(connection, task)
    if not silent:
        print_info(
            f'Domain found : name={domain.name()}, uuidstr={domain.UUIDString()}, id={domain.ID()}, uuid={domain.UUID()}')
    return domain  # cast class to Domain
