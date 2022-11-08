# dependencies : xmltodict 0.13
from __future__ import print_function
from testing import test_all_files_in
import sys
import libvirt
from libvirt_system.libvirt import LibvirtManager
from json_xml import *


def main():
    with open('json_xml/examples/xmldoc_example.xml','r') as f:
        xml = f.read()
    obj = json_to_dict(xml_to_json(xml))
    print(obj)
    pass


def lookup_by_name(name='test_vm_1'):
    manager = LibvirtManager()
    conn = manager.conn
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
