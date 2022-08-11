import sys

sys.path.append('../')

from python_system_tools.docker import Docker
from ptf import testutils
from ptf.base_tests import BaseTest
from data import ip_address, user_name, password, nqn, spdk_port


class TestCreateRamdriveAndAttachAsNsToSubsystem(BaseTest):

    VOLUME_ID = ''

    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        cmd = f'python -c \\\"from scripts.disk_infrastructure import create_ramdrive_and_attach_as_ns_to_subsystem; print(create_ramdrive_and_attach_as_ns_to_subsystem(\'{ip_address}\', \'Malloc0\', 4, \'{nqn}\', {spdk_port}))\\\"'
        volume_id, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
        TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID = volume_id.strip()
        print(TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID)
        assert len(TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID) == 36


    def tearDown(self):
        images = ("ipu-storage-container", "storage-target")
        for image in images:
            container_id = self.proxy_terminal.get_docker_id(docker_image=image)
            self.proxy_terminal.kill_container(container_id)
        self.proxy_terminal.kill_container(self.test_driver_id)

