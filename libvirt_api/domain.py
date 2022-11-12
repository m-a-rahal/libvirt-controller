from __future__ import annotations

from enum import Enum

from libvirt import virDomain

from libvirt_api.exceptions import print_stderr


class DOMAIN_STATE(Enum):
    VIR_DOMAIN_NOSTATE = 0
    VIR_DOMAIN_RUNNING = 1
    VIR_DOMAIN_BLOCKED = 2
    VIR_DOMAIN_PAUSED = 3
    VIR_DOMAIN_SHUTDOWN = 4
    VIR_DOMAIN_SHUTOFF = 5
    VIR_DOMAIN_CRASHED = 6
    VIR_DOMAIN_PMSUSPENDED = 7


def get_info(domain: virDomain):
    info = domain.info()
    if info is None:
        print_stderr(f"can't get info of domain {domain.name()} {domain.UUID()}")
    return info


# get state
def get_state(domain: virDomain) -> DOMAIN_STATE or None:
    """
    returns domain state, might raise exception if info can't be obtained
    :return: domain state
    """
    state, reason = domain.state()
    # if state in domain state accepted values #TODO: 🍀 learn trick : Enums
    if state in DOMAIN_STATE._value2member_map_:
        return DOMAIN_STATE(state)
    else:
        print_stderr(f'The state is unknown. reason code = {reason}')
    return None
