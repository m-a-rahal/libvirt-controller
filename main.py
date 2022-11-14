from __future__ import print_function

import traceback

from libvirt_api.commands import *
from libvirt_api import LibvirtManager
from libvirt_api.json_xml.jsonxmldict import CommandSyntax
from test import load_xml_example


def main():
    # test connection
    manager = LibvirtManager('qemu:///system')
    # use this statement to always close connection at the end
    with manager as connection:
        # test domain creation
        for task in protocol_tasks(name='new_test_vm_100', memory='10'):
            try:
                print_info(f'\n>>> running task: {task[CommandSyntax.command]}')
                domain = manager.receive_task(task)
            except Exception as e:
                print_stderr(e, context="error", raise_exception=False)
                print(traceback.format_exc())

def protocol_alpine_shutdown(**kwargs):
    docDesc = load_xml_example(**kwargs)
    return [
        JsonXmlDict({
            CommandSyntax.command: 'domain_shutdown',
            CommandSyntax.args: {
                'name': 'alpinelinux3.15',
            }
        })
    ]

def protocol_tasks(**kwargs):
    docDesc = load_xml_example(**kwargs)
    return [
        # create VM from XML
        JsonXmlDict({
            CommandSyntax.command: 'createXML',
            CommandSyntax.args: {
                'xmlDesc': docDesc,
                'flags': 0,
            }
        }),
        # pause VM
        JsonXmlDict({
            CommandSyntax.command: 'domain_suspend',
            CommandSyntax.args: {
                'name': 'new_test_vm_100',
            }
        }),
        # resume VM
        JsonXmlDict({
            CommandSyntax.command: 'domain_resume',
            CommandSyntax.args: {
                'name': 'new_test_vm_100',
            }
        }),
        # save VM
        JsonXmlDict({
            CommandSyntax.command: 'domain_save',
            CommandSyntax.args: {
                'name': 'new_test_vm_100',
                'to': 'random_file',
            }
        }),
        # restore VM
        JsonXmlDict({
            CommandSyntax.command: 'domain_restore',
            CommandSyntax.args: {
                'name': 'new_test_vm_100',
                'frm': 'random_file',
            }
        }),
        # shutdown VM (doesn't work without OS)
        JsonXmlDict({
            CommandSyntax.command: 'domain_shutdown',
            CommandSyntax.args: {
                'name': 'new_test_vm_100',
            }
        }),
        # destroy VM
        JsonXmlDict({
            CommandSyntax.command: 'domain_destroy',
            CommandSyntax.args: {
                'name': 'new_test_vm_100',
            }
        }),
        # define VM
        JsonXmlDict({
            CommandSyntax.command: 'defineXML',
            CommandSyntax.args: {
                'xml': docDesc,
            }
        }),
        # start/create VM
        JsonXmlDict({
            CommandSyntax.command: 'domain_create',
            CommandSyntax.args: {
                'name': 'new_test_vm_100',
            }
        }),
        # lookup VM (by name)
        JsonXmlDict({
            CommandSyntax.command: 'lookupByName',
            CommandSyntax.args: {
                'name': 'new_test_vm_100',
            }
        }),
        # lookup by UUID string
        JsonXmlDict({
            CommandSyntax.command: 'lookupByUUID',
            CommandSyntax.args: {
                'uuid': '07aea90a-ad87-4480-b6e2-c2d3bc5ed4ee',
            }
        }),
    ]


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
