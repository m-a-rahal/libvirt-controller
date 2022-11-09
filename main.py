# dependencies : xmltodict 0.13
from __future__ import print_function
from testing import test_all_files_in
import sys
import libvirt
from libvirt_system.libvirt import LibvirtManager
from json_xml import *


def main():
    test1()

def test1():
    with open('json_xml/examples/xmldoc_example.xml', 'r') as f:
        xml = f.read()
    obj = json_to_dict(xml_to_json(xml))
    print(obj)

def test2():
    manager = LibvirtManager()
    conn = manager.connection
    name = 'test_vm_1'
    uuid_str = '45e2aa3d-99fd-4994-a9b4-539414e62171'
    domain = conn.lookupByUUIDString(uuid_str)
    # create domain
    if not domain.isActive():
        domain.create()
    state, reason = domain.state()
    print(f'state : {state}')
    domain.suspend()
    # destroy
    domain.destroy()

def lookup_by_name(name='test_vm_1'):
    manager = LibvirtManager()
    conn = manager.connection
    domain = conn.lookupByUUIDString('45e2aa3d-99fd-4994-a9b4-539414e62171')
    print(domain)
    # create domain
    domain.create()
    # is the domain running
    print(domain.isActive())
    # destroy
    domain.destroy()


if __name__ == '__main__':
    main()
