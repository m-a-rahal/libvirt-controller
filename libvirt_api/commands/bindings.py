from __future__ import annotations
from libvirt_api.commands import *
from libvirt_api.commands.function_enum import FunctionEnum
from libvirt_api.json_xml.jsonxmldict import JsonXmlDict, CommandSyntax as Syntax
"""
DESCRIPTION:
this module maps all the commands to the right functions,
keep it a separate file for clarity, and also because it won't work if you put it above the functions

Here I used Enums () to 
"""

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

    def as_json(self, **args) -> str:
        """create the json format of the command given the arguments"""
        return self.as_dict(**args).json

    def as_xml(self, **args) -> str:
        """create the XML format of the command given the arguments
        this function might not be needed"""
        return self.as_dict(**args).json

    def as_dict(self, **args) -> JsonXmlDict:
        """create the dict (JsonDict) format of the command given the arguments"""
        dict_ = JsonXmlDict({})
        dict_[Syntax.command.value] = self.name
        dict_[Syntax.args.value] = args
        return dict_
