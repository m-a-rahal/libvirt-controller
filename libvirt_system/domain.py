from __future__ import annotations
from libvirt import virDomain
from libvirt_system.exceptions import print_stderr
from libvirt_system.task import Task
import libvirt
from enum import Enum


class DOMAIN_STATE(Enum):  # TODO: 🍀 learn enums
    VIR_DOMAIN_NOSTATE = 0
    VIR_DOMAIN_RUNNING = 1
    VIR_DOMAIN_BLOCKED = 2
    VIR_DOMAIN_PAUSED = 3
    VIR_DOMAIN_SHUTDOWN = 4
    VIR_DOMAIN_SHUTOFF = 5
    VIR_DOMAIN_CRASHED = 6
    VIR_DOMAIN_PMSUSPENDED = 7

class Domain(virDomain):
    states = DOMAIN_STATE

    @staticmethod
    def cast(domain: Domain):  # TODO: 🍀 learn trick, casting (don't cast unless you know what you're doing)
        domain.__class__ = Domain
        return domain

    def get_info(self):
        info = self.info()
        if info is None:
            print_stderr(f"can't get info of domain {self.name()} {self.UUID()}")
        return info

    @staticmethod
    def lookup_domain(connection: libvirt.virConnect, task: Task) -> Domain:
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
        lookup = task.get_or_error('lookup').lower()
        domain: Domain or None = None  # TODO: 🍀 learn trick
        token = None
        if lookup == 'name':
            token = name = task.get_or_error('name')
            domain = connection.lookupByName(name)
        elif lookup == 'uuid_string':  # example: 45e2aa3d-99fd-4994-a9b4-539414e62171
            token = uuid_string = task.get_or_error('uuid_string')
            domain = connection.lookupByUUIDString(uuid_string)
        elif lookup == 'uuid':  # example b'E\xe2\xaa=\x99\xfdI\x94\xa9\xb4S\x94\x14\xe6!q'
            token = uuid = task.get_or_error('uuid')
            domain = connection.lookupByUUID(uuid)
        elif lookup == 'id':
            token = id_ = task.get_or_error('id')
            domain = connection.lookupByID(id_)
        else:
            print_stderr(f'lookup = {lookup} is not a valid/implemented option')
        if domain is None:
            print_stderr(f"domain {lookup}={token} does not exist, or lookup failed")
        return Domain.cast(domain)  # cast class to Domain

    # get state
    def get_state(self) -> DOMAIN_STATE or None:
        """
        returns domain state, might raise exception if info can't be obtained
        :return: domain state
        """
        state, reason = self.state()
        # if state in domain state accepted values #TODO: 🍀 learn trick : Enums
        if state in DOMAIN_STATE._value2member_map_:
            print_stderr(f'state = {DOMAIN_STATE(state).name}', raise_exception=False)
            return DOMAIN_STATE(state)
        else:
            print_stderr(f'The state is unknown. reason code = {reason}')
        return None
