import re
import sys

sys.path.append('../')

from python_system_tools.docker import Docker
from scripts import socket_functions
from ptf import testutils
from ptf.base_tests import BaseTest
from data import ip_address, user_name, password


class TestCreateVirtioBlk64(BaseTest):

    DEVICE_HANDLES = []

    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        print(TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS)
        for physical_id, volume_id in enumerate(TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS):
            cmd = f'python -c \\\"from scripts.disk_infrastructure import create_virtio_blk; print(create_virtio_blk(\'{ip_address}\', \'{volume_id}\', \'{physical_id}\', \'0\', \'{nqn}\', \'{ip_address}\', \'{nvme_port}\', {sma_port}))\\\"'
            device_handle, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
            TestCreateVirtioBlk64.DEVICE_HANDLES.append(device_handle.strip())
        cmd = 'lsblk --output "NAME"'
        out = socket_functions.send_command_over_unix_socket(
            sock=sock, cmd=cmd, wait_for_secs=1
        )
        number_of_virtio_blk_devices = len(re.findall("vd", out))
        print(TestCreateVirtioBlk64.DEVICE_HANDLES)
        print(number_of_virtio_blk_devices)
        assert number_of_virtio_blk_devices == 64

    def tearDown(self):
        pass
