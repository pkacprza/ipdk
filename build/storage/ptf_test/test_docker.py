import json
import sys
from pathlib import Path

sys.path.append('../')

from python_system_tools.extendedterminal import ExtendedTerminal
from python_system_tools.docker import Docker
from ptf import testutils
from ptf.base_tests import BaseTest


class TestImages(BaseTest):

    def setUp(self):
        path = Path.cwd()
        data_path = path.parent / "python_system_tools/data.json"
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.docker_proxy = ExtendedTerminal(
            self.data["proxy_address"], self.data["user"], self.data["password"]
        )

    def runTest(self):
        images = ("test-driver", "traffic-generator", "spdk-app")
        out, _ = self.docker_proxy.execute("docker images")
        for image in images:
            assert image in out

    def tearDown(self):
        pass


class TestGetDockerID(BaseTest):

    def setUp(self):
        path = Path.cwd()
        data_path = path.parent / "python_system_tools/data.json"
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.docker_proxy = Docker(
            self.data["proxy_address"], self.data["user"], self.data["password"]
        )
        self.docker_storage = Docker(
            self.data["storage_address"], self.data["user"], self.data["password"]
        )

    def runTest(self):
        assert self.docker_storage.get_docker_id(self.data["storage_docker_image"]) is not None
        assert self.docker_proxy.get_docker_id(self.data["proxy_docker_image"]) is not None

    def tearDown(self):
        pass


class TestExecuteInDocker(BaseTest):

    def setUp(self):
        path = Path.cwd()
        data_path = path.parent / "python_system_tools/data.json"
        with open(file=data_path) as f:
            self.data = json.load(f)
        self.docker_proxy = Docker(
            self.data["proxy_address"], self.data["user"], self.data["password"]
        )
        self.docker_storage = Docker(
            self.data["storage_address"], self.data["user"], self.data["password"]
        )

    def runTest(self):
        storage_container_id = self.docker_storage.get_docker_id(
            self.data["storage_docker_image"]
        )
        proxy_container_id = self.docker_proxy.get_docker_id(self.data["proxy_docker_image"])
        cmd = "echo Hello, World!"
        out, rc = self.docker_storage.execute_in_docker(
            cmd, storage_container_id, self.data["user"]
        )
        assert out, rc == ("Hello, World!\n", 0)
        out, rc = self.docker_proxy.execute_in_docker(cmd, proxy_container_id, self.data["user"])
        assert out, rc == ("Hello, World!\n", 0)

    def tearDown(self):
        pass

