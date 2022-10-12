import re
import socket
import logging
from ptf.base_tests import BaseTest
from test_connection import BaseTerminalMixin
from system_tools.const import NQN, NVME_PORT, SPDK_PORT, SMA_PORT
from system_tools.ssh_terminal import CommandException
from system_tools.test_platform import StorageTargetPlatform, VirtualMachine

import sys

sys.path.append('../../..')



def send_command_over_unix_socket(sock: str, cmd: str, wait_for_secs: float) -> str:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as s:
        s.settimeout(wait_for_secs),
        out = []
        try:
            s.connect(sock)
            cmd = f"{cmd}\n".encode()
            s.sendall(cmd)
            while data := s.recv(256):
                out.append(data)
        except socket.timeout:
            logging.error("Timeout exceeded")
        return b"".join(out).decode()


def get_docker_containers_id_from_docker_image_name(terminal, docker_image_name):
    out = terminal.execute(f'sudo docker ps | grep "{docker_image_name}"')
    return [line.split()[0] for line in out]


class TestCreateAndExposeSubsystemOverTCP(BaseTerminalMixin, BaseTest):
    def setUp(self):
        super().setUp()
        try:
            out = self.ipu_storage_terminal.execute("sudo netstat -anop | grep '4420 '")
            assert out == []
        except CommandException:
            ...

    def runTest(self):
        container_id = get_docker_containers_id_from_docker_image_name(self.ipu_storage_terminal, "cmd-sender")[0]
        self.ipu_storage_terminal.execute(f'docker exec {container_id} python -c "from scripts.disk_infrastructure import create_and_expose_subsystem_over_tcp; create_and_expose_subsystem_over_tcp(\'{self.storage_target_terminal.config.ip_address}\', \'{NQN}\', \'{NVME_PORT}\', {SPDK_PORT})"')
        out = self.ipu_storage_terminal.execute("sudo netstat -anop | grep '4420 '")
        assert "spdk_tgt" in out[0]

    def tearDown(self):
        """Delete subsystem"""


from system_tools.const import SHARE_DIR_PATH
import os
import time

WORKSPACE_PATH = '/home/berta/ipdk_tests_workdir'
STORAGE_PATH = os.path.join(WORKSPACE_PATH, "ipdk/build/storage")
SHARE_DIR_PATH = os.path.join(WORKSPACE_PATH, SHARE_DIR_PATH)


class TestCreateRamdriveAndAttachAsNsToSubsystem64(BaseTerminalMixin, BaseTest):

    VOLUME_IDS = []


    def setUp(self):
        super().setUp()
        self.terminal = self.storage_target_terminal
        self.cmd_sender_id = get_docker_containers_id_from_docker_image_name(self.terminal, "cmd-sender")[0]

    def runTest(self):
        volume_ids = []
        for i in range(64):
            cmd = f"""docker exec {self.cmd_sender_id} """ \
                  f"""python -c 'from scripts.disk_infrastructure import create_ramdrive_and_attach_as_ns_to_subsystem; """ \
                  f"""print(create_ramdrive_and_attach_as_ns_to_subsystem("{self.terminal.config.ip_address}", "Malloc{i}", 4, "{NQN}", {SPDK_PORT}))'"""
            volume_ids.append(self.terminal.execute(cmd)[0])
        assert len(volume_ids) == 64
        TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS = volume_ids


class TestCreateVirtioBlk64(BaseTerminalMixin, BaseTest):

    DEVICE_HANDLES = []

    def setUp(self):
        super().setUp()
        self.terminal = self.storage_target_terminal
        self.cmd_sender_id = get_docker_containers_id_from_docker_image_name(self.terminal, "cmd-sender")[0]
        self.vm = VirtualMachine(StorageTargetPlatform())
        self.vm.run()
        time.sleep(720)  # change waiting for login
        send_command_over_unix_socket(self.vm.socket_path, "root", 1)
        send_command_over_unix_socket(self.vm.socket_path, "root", 1)

    def runTest(self):
        for physical_id, volume_id in enumerate(TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS):
            cmd = f"""docker exec {self.cmd_sender_id} """\
                  f"""python -c "from scripts.disk_infrastructure import create_virtio_blk; """\
                  f"""print(create_virtio_blk('{self.terminal.config.ip_address}', '{volume_id}', '{physical_id}', '0', '{NQN}', '{self.terminal.config.ip_address}', '{NVME_PORT}', {SMA_PORT}))" """
            device_handle = self.terminal.execute(cmd)[0]
            TestCreateVirtioBlk64.DEVICE_HANDLES.append(device_handle.strip())
        cmd = 'ls -1 /dev'
        out = send_command_over_unix_socket(
            sock=self.vm.socket_path, cmd=cmd, wait_for_secs=1
        )
        number_of_virtio_blk_devices = len(re.findall("vd[a-z]+\\b", out))
        assert number_of_virtio_blk_devices == 64

    def tearDown(self):
        ...
        # self.vm.delete()


class TestDeleteVirtioBlk64(BaseTerminalMixin, BaseTest):
    def setUp(self):
        super().setUp()
        self.terminal = self.storage_target_terminal
        self.cmd_sender_id = get_docker_containers_id_from_docker_image_name(self.terminal, "cmd-sender")[0]
        self.vm = VirtualMachine(StorageTargetPlatform())

    def runTest(self):
        for device_handle in TestCreateVirtioBlk64.DEVICE_HANDLES:
            cmd = f"""docker exec {self.cmd_sender_id} """\
                  f"""python -c "from scripts.disk_infrastructure import delete_virtio_blk; """\
                  f"""print(delete_virtio_blk('{self.terminal.config.ip_address}', '{device_handle}', {SMA_PORT}))" """
            out = self.terminal.execute_in_docker(cmd)[0]
        cmd = 'ls -1 /dev'
        out = send_command_over_unix_socket(
            sock=self.vm.socket_path, cmd=cmd, wait_for_secs=1
        )
        number_of_virtio_blk_devices = len(re.findall("vd[a-z]+\\b", out))
        assert number_of_virtio_blk_devices == 0

    def tearDown(self):
        self.vm.delete()
