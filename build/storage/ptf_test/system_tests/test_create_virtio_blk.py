import re
import sys

sys.path.append('../')

from python_system_tools.docker import Docker
from scripts import socket_functions
from ptf import testutils
from ptf.base_tests import BaseTest
from data import ip_address, user_name, password, sock, nqn, nvme_port, sma_port


class TestCreateVirtioBlk(BaseTest):

    DEVICE_HANDLE = ''

    def setUp(self):
        self.virtual_id = '0'
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        volume_id = TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID
        print(volume_id)
        cmd = f'python -c \\\"from scripts.disk_infrastructure import create_virtio_blk; print(create_virtio_blk(\'{ip_address}\', \'{volume_id}\', \'0\', \'{self.virtual_id}\', \'{nqn}\', \'{ip_address}\', \'{nvme_port}\', {sma_port}))\\\"'
        device_handle, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
        TestCreateVirtioBlk.DEVICE_HANDLE = device_handle.strip()
        cmd = 'lsblk --output "NAME,VENDOR,SUBSYSTEMS"'
        out = socket_functions.send_command_over_unix_socket(
            sock=sock, cmd=cmd, wait_for_secs=1
        )
        number_of_virtio_blk_devices = len(re.findall("block:virtio:pci", out))
        assert number_of_virtio_blk_devices == 1

    def tearDown(self):
        images = ("ipu-storage-container", "storage-target")
        for image in images:
            container_id = self.proxy_terminal.get_docker_id(docker_image=image)
            self.proxy_terminal.kill_container(container_id)
        self.proxy_terminal.kill_container(self.test_driver_id)
