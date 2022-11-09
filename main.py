# dependencies : xmltodict 0.13
from __future__ import print_function
from json_xml import *
from libvirt_system.commands import *
from libvirt_system.libvirt_sys import LibvirtManager
import traceback



def main():
    # testing connection
    manager = LibvirtManager('qemu:///system')
    # use this statement to always close connection at the end
    with manager as connection:
        # testing domain creation
        for task in protocol_tasks(name='new_test_vm_100', memory='10'):
            try:
                print_info(f'\n>>> running task: {task["libvirt_command"]}')
                domain = manager.receive_task(task)
            except Exception as e:
                print(traceback.format_exc())

def protocol_tasks(**kwargs):
    docDesc = get_prop_xml(**kwargs)
    protocol = [
        # create VM from XML
        Task({
            'libvirt_command': 'createXML',
            'libvirt_args': {
                'xmlDesc': docDesc,
                'flags': 0,
            }
        }),
        # pause VM
        Task({
            'libvirt_command': 'domain_suspend',
            'libvirt_args': {
                'name': 'new_test_vm_100',
            }
        }),
        # resume VM
        Task({
            'libvirt_command': 'domain_resume',
            'libvirt_args': {
                'name': 'new_test_vm_100',
            }
        }),
        # save VM
        Task({
            'libvirt_command': 'domain_save',
            'libvirt_args': {
                'name': 'new_test_vm_100',
                'to': 'random_file',
            }
        }),
        # restore VM
        Task({
            'libvirt_command': 'domain_restore',
            'libvirt_args': {
                'name': 'new_test_vm_100',
                'frm': 'random_file',
            }
        }),
        # shutdown VM (doesn't work without OS)
        Task({
            'libvirt_command': 'domain_shutdown',
            'libvirt_args': {
                'name': 'new_test_vm_100',
            }
        }),
        # destroy VM
        Task({
            'libvirt_command': 'domain_destroy',
            'libvirt_args': {
                'name': 'new_test_vm_100',
            }
        }),
        # define VM
        Task({
            'libvirt_command': 'defineXML',
            'libvirt_args': {
                'xml': docDesc,
            }
        }),
        # start/create VM
        Task({
            'libvirt_command': 'domain_create',
            'libvirt_args': {
                'name': 'new_test_vm_100',
            }
        }),
        # lookup VM (by name)
        Task({
            'libvirt_command': 'lookupByName',
            'libvirt_args': {
                'name': 'new_test_vm_100',
            }
        }),
        # lookup by UUID string
        Task({
            'libvirt_command': 'lookupByUUIDString',
            'libvirt_args': {
                'uuidstr': '07aea90a-ad87-4480-b6e2-c2d3bc5ed4ee',
            }
        }),
    ]
    return protocol

def get_prop_xml(**kwargs):
    with open('json_xml/examples/xmldoc_example.xml', 'r') as f:
        doc = f.read()
    doc = Task(xml_to_dict(doc))
    domain = doc['domain']
    for k, v in kwargs.items():
        domain[k] = v
    return doc.xml

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
