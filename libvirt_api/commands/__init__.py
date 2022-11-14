from __future__ import annotations

from enum import Enum

import libvirt
from libvirt import virDomain, virConnect

from libvirt_api.commands.function_enum import FunctionEnum
from libvirt_api.domain import get_state
from libvirt_api.exceptions import print_stderr, print_info, Position
from libvirt_api.json_xml import *
from libvirt_api.json_xml.jsonxmldict import JsonXmlDict


def lookupByName(connection: virConnect, task: JsonXmlDict):
    return _lookup(LookupType.name, connection, task)


def lookupByUUID(connection: virConnect, task: JsonXmlDict):
    return _lookup(LookupType.uuid, connection, task)


def lookupByID(connection: virConnect, task: JsonXmlDict):
    return _lookup(LookupType.id, connection, task)


def _lookup(by: LookupType, connection: virConnect, task: JsonXmlDict):
    x = task.args.get_or_error(by.name, context=f'lookupBy({by.name})')
    # call specified lookup function
    domain: virDomain = by.value(connection, x)
    if domain is None:
        print_stderr(f"domain name={x} does not exist, or lookup failed")
    else:
        print_info(f'Domain found :\n\tname={domain.name()}, uuid={domain.UUIDString()}, id={domain.ID()}')
        print_info(f'\tdomain state = {get_state(domain).name}')
    return domain


def _lookupByUUID(connection: virConnect, task: JsonXmlDict):
    x = task.args.get_or_error('uuid', context=f'lookupByUUIDString(uuid)')
    domain = connection.lookupByUUIDString(x)
    if domain is None:
        print_stderr(f"domain uuid={x} does not exist, or lookup failed")
    return domain


class LookupType(Enum):
    name = FunctionEnum(virConnect.lookupByName)
    id = FunctionEnum(virConnect.lookupByID)
    uuid = FunctionEnum(virConnect.lookupByUUIDString)


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
        print_info(f'Guest {domain.name()} has booted.')
    get_new_state(domain, connection, task)
    return domain


def defineXML(connection: virConnect, task: JsonXmlDict) -> virDomain:
    args = task.args
    domain = connection.defineXML(args.get_or_error('xml', context='defineXML(xml)'))
    if domain is None:
        print_stderr(f'failed to define domain from XML definition')
    else:
        print_stderr(f'Guest {domain.name()} successfully defined.', raise_exception=False)
    # cast domain (virDomain) to Domain class (to have extra functionality)
    return get_new_state(domain, connection, task)


def XMLDesc(connection: virConnect, task: JsonXmlDict, verbose=True) -> str:
    domain = lookup_domain(connection, task)
    flags = task.args.get('flags', 0)
    xml_desc = domain.XMLDesc(flags)
    if verbose:
        print_info(f'domain XMLDesc :\n{xml_desc}')
    return xml_desc


def JSONDesc(connection: virConnect, task: JsonXmlDict) -> str:
    xml_desc = XMLDesc(connection, task, verbose=False)
    json_desc = xml_to_json(xml_desc)
    print_info(f'domain JSONDesc :\n{json_desc}')
    return json_desc


def lookup_domain(connection: libvirt.virConnect, task: JsonXmlDict) -> virDomain:
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
    elif 'name' in args:
        domain = lookupByName(connection, task)
    return domain  # cast class to Domain
