# dependencies : xmltodict 0.13
from __future__ import print_function
from testing import test_all_files_in
import sys
import libvirt
from libvirt_system.libvirt import LibvirtManager
from json_xml import *


def main():
    manager = LibvirtManager()
    conn = manager.connection
    name = 'test'
    domain = conn.lookupByName(name)
    print(domain)
    # create domain
    domain.create()
    # is the domain running
    print(domain.isActive())
    domain.suspend()
    # destroy
    domain.destroy()
    pass


def test1():
    with open('json_xml/examples/xmldoc_example.xml', 'r') as f:
        xml = f.read()
    obj = json_to_dict(xml_to_json(xml))
    print(obj)

def lookup_by_name(name='test_vm_1'):
    manager = LibvirtManager()
    conn = manager.connection
    domain = conn.lookupByName(name)
    print(domain)
    # create domain
    domain.create()
    # is the domain running
    print(domain.isActive())
    # destroy
    domain.destroy()


if __name__ == '__main__':
    main()
