import json
import logging
import os
import re
import sys
import time
from pathlib import Path

sys.path.append('../')

from python_system_tools.extendedterminal import ExtendedTerminal
from python_system_tools.setup import Setup
from scripts.socket_functions import send_command_over_unix_socket
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


class TestRunVM(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.terminal = ExtendedTerminal(self.data["address"], self.data["user"], self.data["password"])

    def runTest(self):
        self.terminal.execute_as_root(cmd='SHARED_VOLUME=/home/berta/IPDK_workspace/SHARE UNIX_SERIAL=vm_socket '
                                      '/home/berta/IPDK_workspace/ipdk/build/storage/scripts/vm/run_vm.sh &'
                                      '> /dev/null &')
        out, _ = self.terminal.execute(cmd="ls /home/berta/IPDK_workspace/SHARE")
        pattern = 'vm(_original)?.qcow2'
        result = re.search(pattern=pattern, string=out)
        if result is None:
            logging.error(f"Cannot find {pattern} in {out}")

        result = result.group(0)
        assert result

        logging.info("")
        time.sleep(120)

        user_out = send_command_over_unix_socket('/home/berta/IPDK_workspace/SHARE/vm_socket', 'root', 2)
        user_login_result = re.search(pattern='Password', string=user_out)
        assert user_login_result
        
        password_result = send_command_over_unix_socket('/home/berta/IPDK_workspace/SHARE/vm_socket', 'root', 10)
        user_password_result = re.search(pattern='root@', string=password_result)
        assert user_password_result
