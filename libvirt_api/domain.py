from __future__ import annotations
from enum import Enum
from libvirt import virDomain
from libvirt_api.exceptions import print_stderr
from libvirt_api.json_xml.jsonxmldict import DataType, JsonXmlDict


class DOMAIN_STATE(Enum):
    VIR_DOMAIN_NOSTATE = 0
    VIR_DOMAIN_RUNNING = 1
    VIR_DOMAIN_BLOCKED = 2
    VIR_DOMAIN_PAUSED = 3
    VIR_DOMAIN_SHUTDOWN = 4
    VIR_DOMAIN_SHUTOFF = 5
    VIR_DOMAIN_CRASHED = 6
    VIR_DOMAIN_PMSUSPENDED = 7  # power management suspended


def get_info(domain: virDomain):
    info = domain.info()
    if info is None:
        print_stderr(f"can't get info of domain {domain.name()} {domain.UUID()}")
    return info

def get_desc(domain: virDomain, flags: int = 0) -> JsonXmlDict:
    xmldesc = domain.XMLDesc(flags)
    return JsonXmlDict(xmldesc, data_type=DataType.xml)

# get state
def get_state(domain: virDomain) -> DOMAIN_STATE:
    """
    returns domain state, might raise exception if info can't be obtained
    :return: domain state
    """
    state, reason = domain.state()
    # if state in domain state accepted values #TODO: 🍀 learn trick : Enums
    # noinspection PyProtectedMember
    if state in DOMAIN_STATE._value2member_map_:
        return DOMAIN_STATE(state)
    else:
        print_stderr(f'The state is unknown. reason code = {reason}')

def domain_matches_xmlDesc(domain: virDomain, xmlDesc: str):
    self_xmlDesc = get_desc(domain)
    # TODO: implement xml matching
    if self_xmlDesc == xmlDesc:
        pass
    return True
