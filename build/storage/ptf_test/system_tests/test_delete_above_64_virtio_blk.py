import re
import sys

sys.path.append('../')

from python_system_tools.docker import Docker
from scripts import socket_functions
from ptf import testutils
from ptf.base_tests import BaseTest
from data import ip_address, user_name, password, sock


class TestDeleteVirtioBlkAbove64(BaseTest):
    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        print(TestCreateVirtioBlkAbove64.DEVICE_HANDLES)
        for device_handle in TestCreateVirtioBlkAbove64.DEVICE_HANDLES:
            cmd = f'python -c \\\"from scripts.disk_infrastructure import delete_virtio_blk; print(delete_virtio_blk(\'{ip_address}\', \'{device_handle}\', {sma_port}))\\\"'
            out, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
        cmd = 'lsblk --output "NAME"'
        out = socket_functions.send_command_over_unix_socket(
            sock=sock, cmd=cmd, wait_for_secs=1
        )
        number_of_virtio_blk_devices = len(re.findall("vd", out))
        assert number_of_virtio_blk_devices == 0

    def tearDown(self):
        pass
