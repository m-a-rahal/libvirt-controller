# #unit_test_tutorial: https://machinelearningmastery.com/a-gentle-introduction-to-unit-testing-in-python)
import os.path
import unittest
from dataclasses import dataclass

from libvirt_api import LibvirtManager
from libvirt_api.commands.bindings import *
from libvirt_api.domain import DOMAIN_STATE, domain_matches_xmlDesc
from libvirt_api.exceptions import CantCreateDomainError
from tests import load_xml_example, load_xml_examples, create_n_domains, TempDomain


class TestScenarios:
    class SaveLoadFile:
        """this creates a file for saving and loading a domain
        this class was created to remove file creation/deletion/checking from the tests """
        default = 'random_file'

        def __init__(self, file: str = None):
            if file is None:
                file = TestScenarios.SaveLoadFile.default
            self.file = file

        def __enter__(self) -> str:
            # if the file exists, don't override it ! might be an important file.
            assert not os.path.exists(
                self.file), f"the file '{self.file}' already exists, please choose an empty path to test " \
                            f"domain saving and loading "
            return self.file

        def __exit__(self, exc_type, exc_val, exc_tb):
            file = self.file
            # delete file
            if os.path.exists(file):
                os.remove(file)
            assert not os.path.exists(file), f"file {file} was not deleted properly!"


class TestCommands(unittest.TestCase):
    # ====================================================================================================
    # PRIVATE METHODS ====================================================================================
    # ====================================================================================================
    def run_command(self, command: Command, **args):
        json_command = command.as_json(**args)
        return self.manager.receive_task(json_command)

    # ====================================================================================================
    # METHODS CALLED BEFORE AND AFTER TESTS ==============================================================
    # ====================================================================================================
    manager: LibvirtManager = None
    domain_lookup_test: virDomain = None
    domain_state_change_test: virDomain = None

    @classmethod
    def setUpClass(cls) -> None:
        """called before all tests once """
        # create libvirt a new libvirt manager
        cls.manager = LibvirtManager()
        # create 2 domains
        domains = create_n_domains(2)
        # one to test lookups
        cls.domain_lookup_test = domains.pop()
        # another to test state changes, TODO: need OS here, try to make alpine work (for now use simple domain)
        cls.domain_state_change_test = domains.pop()

    @classmethod
    def tearDownClass(cls) -> None:
        """called after all tests are done"""
        # destroy temporary structures
        cls.domain_lookup_test.destroy()
        cls.domain_state_change_test.destroy()

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
            domain: virDomain = self.run_command(command, **args)
            # assert domains are equal with UUID
            self.assertEqual(domain.UUIDString(), self.domain_lookup_test.UUIDString())

    def test_open_connection(self):
        manager = self.manager
        # test creation of a standard connection
        json_command = Command.open_connection.as_json()
        conn = self.run_command(Command.open_connection, name=LibvirtManager.default_connection_uri)
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
                domain: virDomain = self.run_command(Command.createXML, xmlDesc=xml_desc_example, flags=0)
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

    def test_domain_suspend_and_resume(self):
        domain = self.domain_state_change_test
        # suspend domain and see if it suspends (new state)
        new_state = self.run_command(Command.domain_suspend, uuid=domain.UUIDString())
        self.assertEqual(new_state, DOMAIN_STATE.VIR_DOMAIN_PAUSED)
        # resume domain and see if it resumes (new state)
        new_state = self.run_command(Command.domain_resume, uuid=domain.UUIDString())
        self.assertEqual(new_state, DOMAIN_STATE.VIR_DOMAIN_RUNNING)

    def test_domain_save_and_restore(self):
        # ⚠ this
        with TempDomain(self.connection) as domain:  # create temporary domain
            # save domain and see if it works (TODO: 🟠 how ?)
            file_scope = TestScenarios.SaveLoadFile()
            with file_scope as file:  # this will create the file, then delete it after use
                try:
                    new_state = self.run_command(Command.domain_save, to=file, uuid=domain.UUIDString())
                except exceptions.FailedToGetState as e:
                    pass  # expected behavior
                self.assertTrue(os.path.exists(file),
                                "the save file for the domain was not created, domain was not saved")
                # restore domain and see if it resumes (new state)
                try:
                    new_state = self.run_command(Command.domain_restore, frm=file, uuid=domain.UUIDString())
                except exceptions.FailedToSaveDomain:
                    self.fail('failed to load domain')
                self.assertEqual(new_state, DOMAIN_STATE.VIR_DOMAIN_RUNNING)

    def test_domain_create(self):
        """start a domain that was previously defined, and see if description matches"""
        with self.manager as connection:
            raise Exception('unimplemented')
            # TODO: create this tests

    def test_domain_shutdown(self):
        with TempDomain(self.connection) as domain:
            first_state = get_state(domain)
            assert first_state == DOMAIN_STATE.VIR_DOMAIN_RUNNING, "created domain is not running"
            uuid = domain.UUIDString()
            domain: virDomain = self.run_command(Command.domain_shutdown, uuid=uuid)
            new_state = get_state(domain)
            self.assertNotEqual(first_state, new_state, "the domain is still running")

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
