import json
import re
import sys
from pathlib import Path

sys.path.append('../')

from python_system_tools.docker import Docker
from scripts import socket_functions
from ptf import testutils
from ptf.base_tests import BaseTest


path = Path.cwd()
data_path = path.parent / "python_system_tools/data.json"
with open(file=data_path) as f:
    data = json.load(f)
ip_address = data["proxy_address"]
user_name = data["user"]
password = data['password']
nqn = 'nqn.2016-06.io.spdk:cnode0'
spdk_port = 5260
nvme_port = '4420'
sma_port = 8080
sock = '/home/berta/IPDK_workspace/SHARE/vm_socket'

class TestCreateAndExposeSubsystemOverTCP(BaseTest):

    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        self.proxy_terminal.execute_in_docker(f'python -c \\\"from scripts.disk_infrastructure import create_and_expose_subsystem_over_tcp; create_and_expose_subsystem_over_tcp(\'{ip_address}\', \'{nqn}\', \'{nvme_port}\', {spdk_port})\\\"', container_id=self.test_driver_id, raise_on_error=False)

    def tearDown(self):
        pass


class TestCreateRamdriveAndAttachAsNsToSubsystem(BaseTest):

    VOLUME_ID = ''

    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        cmd = f'python -c \\\"from scripts.disk_infrastructure import create_ramdrive_and_attach_as_ns_to_subsystem; print(create_ramdrive_and_attach_as_ns_to_subsystem(\'{ip_address}\', \'Malloc0\', 16, \'{nqn}\', {spdk_port}))\\\"'
        volume_id, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
        TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID = volume_id.strip()
        print(TestCreateRamdriveAndAttachAsNsToSubsystem.VOLUME_ID)


    def tearDown(self):
        pass


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
        pass


class TestDeleteVirtioBlk(BaseTest):
    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")


    def runTest(self):
        print(TestCreateVirtioBlk.DEVICE_HANDLE)
        cmd = f'python -c \\\"from scripts.disk_infrastructure import delete_virtio_blk; print(delete_virtio_blk(\'{ip_address}\', \'{TestCreateVirtioBlk.DEVICE_HANDLE}\', {sma_port}))\\\"'
        out, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
        assert out.strip() == '0'
        cmd = 'lsblk --output "NAME,VENDOR,SUBSYSTEMS"'
        out = socket_functions.send_command_over_unix_socket(
            sock=sock, cmd=cmd, wait_for_secs=1
        )
        number_of_virtio_blk_devices = len(re.findall("block:virtio:pci", out))
        assert number_of_virtio_blk_devices == 0

    def tearDown(self):
        pass

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

    def tearDown(self):
        pass

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

class TestDeleteVirtioBlk64(BaseTest):
    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        print(TestCreateVirtioBlk64.DEVICE_HANDLES)
        for device_handle in TestCreateVirtioBlk64.DEVICE_HANDLES:
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

class TestCreateRamdriveAndAttachAsNsToSubsystemAbove64(BaseTest):

    VOLUME_IDS = []

    def setUp(self):
        self.proxy_terminal = Docker(
            ip_address, user_name, password
        )
        self.test_driver_id = self.proxy_terminal.get_docker_id(docker_image="test-driver")

    def runTest(self):
        for i in range(65):
            cmd = f'python -c \\\"from scripts.disk_infrastructure import create_ramdrive_and_attach_as_ns_to_subsystem; print(create_ramdrive_and_attach_as_ns_to_subsystem(\'{ip_address}\', \'Malloc{i}\', 4, \'{nqn}\', {spdk_port}))\\\"'
            volume_id, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
            TestCreateRamdriveAndAttachAsNsToSubsystemAbove64.VOLUME_IDS.append(volume_id.strip())
        print(TestCreateRamdriveAndAttachAsNsToSubsystemAbove64.VOLUME_IDS)
        print(len(TestCreateRamdriveAndAttachAsNsToSubsystemAbove64.VOLUME_IDS))

    def tearDown(self):
        pass

