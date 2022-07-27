import json
import sys
import os
from pathlib import Path

sys.path.append('../')

from python_system_tools.docker import Docker
from scripts.disk_infrastructure import create_and_expose_subsystem_over_tcp, \
    create_ramdrive_and_attach_as_ns_to_subsystem, create_virtio_blk
from ptf import testutils
from ptf.base_tests import BaseTest


class TestCreateAndExposeSubsystemOverTCP(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)

        self.ip_address = self.data["proxy_address"]
        self.user_name = self.data["user"]
        self.password = self.data['password']
        self.nqn = "nqn.2016-06.io.spdk:cnode0"
        self.spdk_port = 5260
        self.nvme_port = 4420

        self.proxy_terminal = Docker(
            self.ip_address, self.user_name, self.password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        cmd = f"cd /workspace/ipdk/build/storage/python_system_tools && python -c \\\"from scripts.disk_infrastructure import " \
              f"create_and_expose_subsystem_over_tcp; create_and_expose_subsystem_over_tcp({self.ip_address}, " \
              f"{self.nqn}, {self.nvme_port}, {self.spdk_port})\\\""
        out, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id)

    def tearDown(self):
        pass


class TestCreateRamdriveAndAttachAsNsToSubsystem(BaseTest):

    VOLUME_ID = ""

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)

        self.ip_address = self.data["proxy_address"]
        self.user_name = self.data["user"]
        self.password = self.data['password']
        self.nqn = "nqn.2016-06.io.spdk:cnode0"
        self.spdk_port = 5260

        self.proxy_terminal = Docker(
            self.ip_address, self.user_name, self.password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        for n_ramdrive in range(64):
            cmd = f"cd /workspace/ipdk/build/storage/ && python -c \\\"from scripts.disk_infrastructure import " \
                  "create_ramdrive_and_attach_as_ns_to_subsystem; print(create_ramdrive_and_attach_as_ns_to_subsystem(" \
                  f"{self.ip_address}, 'Malloc{n_ramdrive}', {(n_ramdrive+1)*16}, {self.nqn}, {self.spdk_port}))\\\""
            volume_id, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id)
            self.VOLUME_ID = volume_id

    def tearDown(self):
        pass


class TestCreateVirtioBlk(BaseTest):

    def setUp(self):
        path = Path(os.getcwd())
        data_path = os.path.join(path.parent.absolute(), "python_system_tools/data.json")
        with open(file=data_path) as f:
            self.data = json.load(f)

        self.ip_address = self.data["proxy_address"]
        self.user_name = self.data["user"]
        self.password = self.data['password']
        self.nqn = "nqn.2016-06.io.spdk:cnode0"
        self.spdk_port = 5260
        self.virtual_id = 0
        self.nvme_port = 4420
        self.sma_port = 8080

        self.proxy_terminal = Docker(
            self.ip_address, self.user_name, self.password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        volume_id = TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID
        for n_virtio_blk in range(64):
            cmd = f"cd /workspace/ipdk/build/storage/ && python -c \\\"from scripts.disk_infrastructure import " \
                  f"create_virtio_blk; print(create_virtio_blk({self.ip_address}, {volume_id}, '{n_virtio_blk}', " \
                  f"{self.virtual_id}, {self.nqn}, {self.ip_address}, {self.nvme_port}, {self.sma_port}))\\\""
            out, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id)


    def tearDown(self):
        pass
