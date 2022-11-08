from __future__ import print_function
import argparse
import os
import time
import libvirt

# setup
"""A function for running an SSH command on an active or inactive domain. """
uri = 'qemu:///system'
startupWait = 60 # seconds


def toIPAddressType(address_type):
    if address_type == libvirt.VIR_IP_ADDR_TYPE_IPV4:
        return 'ipv4'
    elif address_type == libvirt.VIR_IP_ADDR_TYPE_IPV6:
        return 'ipv6'

def runJob(domain_name, userid, cmd, restore_file='', open_connx=None):
    # get the connection
    if open_connx is None :
        connx = libvirt.open(uri)
    else:
        connx = open_connx
    # get the domain
    domain = connx.lookupByName(domain_name)
    if domain_name is None:
        if open_connx is None:
            connx.close()
        return
    # start/restore the domain if necessary
    
