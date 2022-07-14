import json
import os
import sys
from pathlib import Path

sys.path.append('../')

from python_system_tools.extendedterminal import ExtendedTerminal
from ptf import testutils
from ptf.base_tests import BaseTest


class TestExecute(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.terminal = ExtendedTerminal(self.data["address"], self.data["user"], self.data["password"])

    def runTest(self):
        assert self.terminal.execute("whoami") == (f"{self.data['user']}\n", 0)

    def tearDown(self):
        pass

class TestExecuteAsRoot(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.terminal = ExtendedTerminal(self.data["address"], self.data["user"], self.data["password"])

    def runTest(self):
        assert self.terminal.execute_as_root("whoami") == (f"root\n", 0)

    def tearDown(self):
        pass

class TestMkdir(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.terminal = ExtendedTerminal(self.data["address"], self.data["user"], self.data["password"])

    def runTest(self):
        path = "~/empty_test_folder"
        self.terminal.mkdir(path)
        out, _ = self.terminal.execute("ls ~/")
        assert "empty_test_folder" in out
        assert self.terminal.execute("rmdir ~/empty_test_folder")[1] == 0

    def tearDown(self):
        pass

