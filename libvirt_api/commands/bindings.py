from __future__ import annotations
from libvirt_api.commands import *
from libvirt_api.commands.function_enum import FunctionEnum
from libvirt_api.json_xml.jsonxmldict import JsonXmlDict, CommandSyntax as Syntx


# TODO: 🔴[📨response] each response must identify the destination, so include that somewhere somehow
class Command(Enum):
    # lookups
    lookupByName = FunctionEnum(lookupByName)
    lookupByID = FunctionEnum(lookupByID)
    lookupByUUID = FunctionEnum(lookupByUUID)
    # connection
    open_connection = FunctionEnum(open_connection)
    # domain (VM) state change, TODO: 🔴[📨response] all these must respond with new domain info (or error)
    defineXML = FunctionEnum(defineXML)  # define + RUN domain
    createXML = FunctionEnum(createXML)  # define domain
    domain_suspend = FunctionEnum(domain_suspend)  # suspend domain
    domain_resume = FunctionEnum(domain_resume)  # resume domain
    domain_save = FunctionEnum(domain_save)  # save domain
    domain_restore = FunctionEnum(domain_restore)  # restore saved domain
    domain_create = FunctionEnum(domain_create)  # start a defined domain
    domain_shutdown = FunctionEnum(domain_shutdown)  # shutdown domain
    domain_destroy = FunctionEnum(domain_destroy)  # destroy domain
    # domain other operations
    domain_get_state = FunctionEnum(domain_get_state)

    # TODO: 🟡 are there other state changes ?

    @classmethod
    def parse(cls, command_str) -> Command or None:
        """returns enum for provided command string, or None"""
        return cls._member_map_.get(command_str, None)

    def json(self, **args) -> str:
        """create the json format of the command given the arguments"""
        json_dict = JsonXmlDict({})
        json_dict[Syntx.command] = self.name
        json_dict[Syntx.args] = args
        return json_dict.json
