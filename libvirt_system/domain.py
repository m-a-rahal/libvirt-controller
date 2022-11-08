from __future__ import annotations
from libvirt import virDomain
from libvirt_system.exceptions import print_stderr, UnrecognizedOption
from libvirt_system.task import Task
import libvirt


class Domain(virDomain):
    def get_info(self):
        info = self.info()
        if info is None:
            print_stderr("can't get info of domain")
        return info

    @staticmethod
    def lookup_domain(connection, task: Task) -> Domain:
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
        domain: Domain
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
        domain.__class__ = Domain  # cast class to Domain
        return domain
