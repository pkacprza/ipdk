import sys

sys.path.append('../')

from python_system_tools.docker import Docker
from scripts import socket_functions
from ptf import testutils
from ptf.base_tests import BaseTest
from data import ip_address, user_name, password, nqn, spdk_port


class TestCreateRamdriveAndAttachAsNsToSubsystem64(BaseTest):

    VOLUME_IDS = []

    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        for i in range(64):
            cmd = f'python -c \\\"from scripts.disk_infrastructure import create_ramdrive_and_attach_as_ns_to_subsystem; print(create_ramdrive_and_attach_as_ns_to_subsystem(\'{ip_address}\', \'Malloc{i}\', 4, \'{nqn}\', {spdk_port}))\\\"'
            volume_id, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
            TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS.append(volume_id.strip())
        print(TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS)
        assert len(TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS) == 64

    def tearDown(self):
        images = ("ipu-storage-container", "storage-target")
        for image in images:
            container_id = self.proxy_terminal.get_docker_id(docker_image=image)
            self.proxy_terminal.kill_container(container_id)
        self.proxy_terminal.kill_container(self.test_driver_id)

