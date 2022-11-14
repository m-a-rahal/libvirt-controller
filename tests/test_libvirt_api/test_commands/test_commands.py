# #unit_test_tutorial: https://machinelearningmastery.com/a-gentle-introduction-to-unit-testing-in-python)

import unittest
from dataclasses import dataclass

import libvirt_api
from libvirt_api import LibvirtManager
from libvirt_api.commands.bindings import *
from libvirt_api.domain import DOMAIN_STATE, domain_matches_xmlDesc
from libvirt_api.exceptions import CantCreateDomainError
from tests import load_xml_example, load_xml_examples, create_test_domain
import sys


class TestCommands(unittest.TestCase):
    # ====================================================================================================
    # METHODS CALLED BEFORE AND AFTER TESTS ==============================================================
    # ====================================================================================================
    manager: LibvirtManager = None
    domain_lookup_test: virDomain = None

    @classmethod
    def setUpClass(cls) -> None:
        """called before all tests once """
        # create libvirt a new libvirt manager
        cls.manager = LibvirtManager()
        # create domain to test lookups
        with cls.manager as conn:
            cls.domain_lookup_test = create_test_domain(conn)

    @classmethod
    def tearDownClass(cls) -> None:
        """called after all tests are done"""
        # destroy temporary structures
        cls.domain_lookup_test.destroy()

    def setUp(self) -> None:
        """called before every tests"""
        # open new default connection to libvirt
        self.connection = self.manager.__enter__()

    def tearDown(self) -> None:
        """called after every tests"""
        self.connection.close()

    # ====================================================================================================
    # COMMAND TESTS ======================================================================================
    # ====================================================================================================
    def test_lookup(self):
        dummy = self.domain_lookup_test  # domain used for test
        setup = zip(
            [Command.lookupByID, Command.lookupByUUID, Command.lookupByName],
            [dict(id=dummy.ID()), dict(uuid=dummy.UUIDString()), dict(name=dummy.name())]
        )
        """lookup domain and test if they have the same UUID"""
        for command, args in setup:
            json_commmand = command.json(**args)
            domain: virDomain = self.manager.receive_task(json_commmand)
            # assert domains are equal with UUID
            self.assertEqual(domain.UUIDString(), self.domain_lookup_test.UUIDString())

    def test_open_connection(self):
        manager = self.manager
        # test creation of a standard connection
        json_command = Command.open_connection.json()
        conn = manager.create_connection_to_libvirt(manager.default_connection_uri)
        self.assertIsNotNone(conn, "connection failed to create")

    def test_open_connection_remote(self):
        raise Exception('unimplemented')

    def test_defineXML(self):
        raise Exception('unimplemented')

    def test_createXML(self):
        """create & run via createXML a domain, and verify if :
                - domain is created and is running
                - generated XML info matches (or mostly matches) the one requested"""
        with self.manager as connection:
            # load an example xml_desc
            for i, xml_desc_example in enumerate(load_xml_examples()):
                print('testing on example', i)
                # call createXMl
                command = Command.createXML.json(xmlDesc=xml_desc_example, flags=0)
                domain: virDomain = self.manager.receive_task(command)
                # testing
                # is domain good None ? and is it good type
                self.assertIsNotNone(domain, f"domain = None (failed to create) after createXMl with example {i}")
                self.assertIsInstance(domain, virDomain, f"command returned the wrong type: {type(domain)}, expected "
                                                         f"virDomain")
                # is domain running
                state = get_state(domain)
                self.assertEqual(state, DOMAIN_STATE.VIR_DOMAIN_RUNNING)
                # assert that created VM has same description as intended
                self.assertTrue(domain_matches_xmlDesc(domain, xml_desc_example), "VM has different description than "
                                                                                  "described in XML creation command")
                # destroy test domain
                print('deleting test domain')
                domain.destroy()

    def test_domain_suspend(self):
        raise Exception('unimplemented')

    def test_domain_resume(self):
        raise Exception('unimplemented')

    def test_domain_save(self):
        raise Exception('unimplemented')

    def test_domain_restore(self):
        raise Exception('unimplemented')

    def test_domain_create(self):
        """start a domain that was previously defined, and see if description matches"""
        with self.manager as connection:
            raise Exception('unimplemented')
            # TODO: create this tests

    def test_domain_shutdown(self):
        raise Exception('unimplemented')

    def test_domain_destroy(self):
        raise Exception('unimplemented')

    def test_domain_get_state(self):
        raise Exception('unimplemented')


@dataclass
class LookupSetup:
    """this class creates a setup for the lookup functions"""
    domain: virDomain
    uuid: str
    id: int
    name: str = 'test_lookup_vm'

    def __enter__(self, ctx: TestCommands):
        """
        find domain, if it's already defined,
        """
        conn = ctx.connection
        domain = conn.lookupByName(self.name)
        domain.destroyFlags()
        if domain is None:
            domain = createXML(conn, JsonXmlDict(load_xml_example(name='test_lookup')))
            if domain is None:
                raise CantCreateDomainError(f"failed to create domain with name={self.name}")
        else:
            get_state(domain)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.domain.destroy()


if __name__ == '__main__':
    unittest.main()
