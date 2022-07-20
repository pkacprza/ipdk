import json
import os
import sys
from pathlib import Path

sys.path.append('../')

from python_system_tools.extendedterminal import ExtendedTerminal
from python_system_tools.setup import Setup
from ptf import testutils
from ptf.base_tests import BaseTest


class TestOS(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.setup_storage = Setup(
            ExtendedTerminal(self.data["storage_address"], self.data["user"], self.data["password"]))
        self.setup_proxy = Setup(ExtendedTerminal(self.data["proxy_address"], self.data["user"], self.data["password"]))

    def runTest(self):
        assert self.setup_storage.os in ("Fedora", "Ubuntu")
        assert self.setup_proxy.os in ("Fedora", "Ubuntu")

    def tearDown(self):
        pass


class TestPM(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.setup_storage = Setup(
            ExtendedTerminal(self.data["storage_address"], self.data["user"], self.data["password"]))
        self.setup_proxy = Setup(ExtendedTerminal(self.data["proxy_address"], self.data["user"], self.data["password"]))

    def runTest(self):
        assert self.setup_storage.pm in ("dnf", "apt")
        assert self.setup_proxy.pm in ("dnf", "apt")

    def tearDown(self):
        pass


class TestCheckVirtualization(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.setup_storage = Setup(
            ExtendedTerminal(self.data["storage_address"], self.data["user"], self.data["password"]))
        self.setup_proxy = Setup(ExtendedTerminal(self.data["proxy_address"], self.data["user"], self.data["password"]))

    def runTest(self):
        return_values = Setup.setup_on_both_machines(
            self.setup_storage.check_virtualization,
            self.setup_proxy.check_virtualization,
            timeout=30,
        )

        assert return_values == (True, True)

    def tearDown(self):
        pass


class TestCheckKVM(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.setup_storage = Setup(
            ExtendedTerminal(self.data["storage_address"], self.data["user"], self.data["password"]))
        self.setup_proxy = Setup(ExtendedTerminal(self.data["proxy_address"], self.data["user"], self.data["password"]))

    def runTest(self):
        return_values = Setup.setup_on_both_machines(
            self.setup_storage.check_kvm,
            self.setup_proxy.check_kvm,
            timeout=30
        )

        assert return_values == (True, True)

    def tearDown(self):
        pass


class TestSetupDockerCompose(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.setup_storage = Setup(
            ExtendedTerminal(self.data["storage_address"], self.data["user"], self.data["password"]))
        self.setup_proxy = Setup(ExtendedTerminal(self.data["proxy_address"], self.data["user"], self.data["password"]))

    def runTest(self):
        return_values = Setup.setup_on_both_machines(
            self.setup_storage.setup_docker_compose,
            self.setup_proxy.setup_docker_compose,
            timeout=60,
        )

        assert return_values == (True, True)

    def tearDown(self):
        pass


class TestSetupLibguestfsTools(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.setup_storage = Setup(
            ExtendedTerminal(self.data["storage_address"], self.data["user"], self.data["password"]))
        self.setup_proxy = Setup(ExtendedTerminal(self.data["proxy_address"], self.data["user"], self.data["password"]))

    def runTest(self):
        return_values = Setup.setup_on_both_machines(
            self.setup_storage.setup_libguestfs_tools,
            self.setup_proxy.setup_libguestfs_tools,
            timeout=30,
        )

        assert return_values == (True, True)

    def tearDown(self):
        pass


class TestInstalled(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.setup_storage = Setup(
            ExtendedTerminal(self.data["storage_address"], self.data["user"], self.data["password"]))
        self.setup_proxy = Setup(ExtendedTerminal(self.data["proxy_address"], self.data["user"], self.data["password"]))

    def runTest(self):
        return_values = Setup.setup_on_both_machines(
            self.setup_storage.is_installed,
            self.setup_proxy.is_installed,
            timeout=60,
        )

        assert return_values == ([0, 0, 0], [0, 0, 0])

    def tearDown(self):
        pass


class TestCheckSecurityPolicies(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.setup_storage = Setup(
            ExtendedTerminal(self.data["storage_address"], self.data["user"], self.data["password"]))
        self.setup_proxy = Setup(ExtendedTerminal(self.data["proxy_address"], self.data["user"], self.data["password"]))

    def runTest(self):
        return_values = Setup.setup_on_both_machines(
            self.setup_storage.check_security_policies,
            self.setup_proxy.check_security_policies,
            timeout=30,
        )

        assert return_values == (True, True)

    def tearDown(self):
        pass
