import json
import os
import sys
from pathlib import Path

sys.path.append('../')

from python_system_tools.extendedterminal import ExtendedTerminal
from python_system_tools.containers_deploy import ContainersDeploy
from python_system_tools.setup import Setup
from ptf import testutils
from ptf.base_tests import BaseTest


class TestRunDockersContainers(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        proxy_terminal = ExtendedTerminal(
            self.data["proxy_address"], self.data["user"], self.data["password"]
        )
        storage_terminal = ExtendedTerminal(
            self.data["storage_address"], self.data["user"], self.data["password"]
        )
        self.containers_deploy = ContainersDeploy(proxy_terminal, storage_terminal)

    def runTest(self):
        assert self.containers_deploy.run_docker_containers() == [0, 0]

    def tearDown(self):
        pass
