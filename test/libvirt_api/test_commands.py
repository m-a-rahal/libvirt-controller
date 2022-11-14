# #unit_test_tutorial: https://machinelearningmastery.com/a-gentle-introduction-to-unit-testing-in-python)
import unittest
from libvirt_api.commands import *
from libvirt_api.exceptions import CantCreateDomainError
from libvirt_api.json_xml.jsonxmldict import CommandSyntax
from test import load_xml_example, load_xml_examples
from libvirt_api import LibvirtManager, Command
from dataclasses import dataclass


class TestCommands(unittest.TestCase):
    # ====================================================================================================
    # METHODS CALLED BEFORE AND AFTER TESTS ==============================================================
    # ====================================================================================================

    @classmethod
    def setUpClass(cls) -> None:
        """called before all tests once """
        # create libvirt a new libvirt manager
        cls.manager = LibvirtManager()

    def setUp(self) -> None:
        """called before every test"""
        # open new default connection to libvirt
        self.connection = self.manager.__enter__()

    def tearDown(self) -> None:
        """called after every test"""
        self.connection.close()

    # ====================================================================================================
    # COMMAND TESTS ======================================================================================
    # ====================================================================================================
    def test_lookupByName(self):
        pass

    def test_lookupByID(self):
        pass

    def test_lookupByUUID(self):
        pass

    def test_open_connection(self):
        pass

    def test_defineXML(self):
        pass

    def test_createXML(self):
        """create & run via createXML a domain, and verify if :
                - domain is created and is running
                - generated XML info matches (or mostly matches) the one requested"""
        with self.manager as connection:
            # load an example xml_desc
            for xml_desc_example in load_xml_examples():
                # call createXMl
                domain = Command.createXML.json(xmlDesc=xml_desc_example, flags=0)
            # TODO: make this test
            # self.assertTrue(domain is running)
            # self.assertTrue(domain matches xml)

    def test_domain_suspend(self):
        pass

    def test_domain_resume(self):
        pass

    def test_domain_save(self):
        pass

    def test_domain_restore(self):
        pass

    def test_domain_create(self):
        """start a domain that was previously defined, and see if description matches"""
        with self.manager as connection:
            pass
            # TODO: create this test

    def test_domain_shutdown(self):
        pass

    def test_domain_destroy(self):
        pass

    def test_domain_get_state(self):
        pass


@dataclass
class LookupSetup:
    """this class creates a setup for the lookup functions"""
    domain: virDomain
    uuid: str
    id: int
    name: str = 'test_lookup_vm'

    def __enter__(self, ctx : TestCommands):
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