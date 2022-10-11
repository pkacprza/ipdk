import re
import socket
import logging
from ptf.base_tests import BaseTest
from test_connection import BaseTerminalMixin
from system_tools.const import NQN, NVME_PORT, SPDK_PORT
from system_tools.ssh_terminal import CommandException


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
            out = self.ipu_storage_terminal.execute("sudo netstat -anop | grep 4420")
            assert out == []
        except CommandException:
            ...

    def runTest(self):
        container_id = get_docker_containers_id_from_docker_image_name(self.ipu_storage_terminal, "cmd-sender")[0]
        self.ipu_storage_terminal.execute(f'docker exec {container_id} python -c "from scripts.disk_infrastructure import create_and_expose_subsystem_over_tcp; create_and_expose_subsystem_over_tcp(\'{self.storage_target_terminal.config.ip_address}\', \'{NQN}\', \'{NVME_PORT}\', {SPDK_PORT})"')
        out = self.ipu_storage_terminal.execute("sudo netstat -anop | grep 4420")
        assert "spdk_tgt" in out[0]

    def tearDown(self):
        """Delete subsystem"""


from system_tools.const import SHARE_DIR_PATH
import os
import time

WORKSPACE_PATH = '/home/berta/ipdk_tests_workdir'
STORAGE_PATH = os.path.join(WORKSPACE_PATH, "ipdk/build/storage")
SHARE_DIR_PATH =os.path.join(WORKSPACE_PATH, SHARE_DIR_PATH)


class TestCreateRamdriveAndAttachAsNsToSubsystem64(BaseTerminalMixin, BaseTest):

    VOLUME_IDS = []

    def setUp(self):
        super().setUp()

        self.terminal = self.ipu_storage_terminal
        t = 60
        pattern = 'vm.qcow2'
        out = ''.join(self.terminal.execute(cmd=f"ls {SHARE_DIR_PATH}"))
        result = re.search(pattern=pattern, string=out)
        if result is None:
            t = 420
        cmd = f'sudo SHARED_VOLUME={SHARE_DIR_PATH} UNIX_SERIAL=vm_socket scripts/vm/run_vm.sh &> /dev/null &'
        self.terminal.execute(f"cd {STORAGE_PATH} && {cmd}")
        time.sleep(t)
        out = ''.join(self.terminal.execute(cmd=f"ls {SHARE_DIR_PATH}"))
        result = re.search(pattern=pattern, string=out)
        assert result

        user_out = send_command_over_unix_socket(f'{os.path.join(SHARE_DIR_PATH, "vm_socket")}', 'root', 2)
        user_login_result = re.search(pattern='Password', string=user_out)
        assert user_login_result

        password_result = send_command_over_unix_socket(f'{os.path.join(SHARE_DIR_PATH, "vm_socket")}', 'root', 2)
        user_password_result = re.search(pattern='root@', string=password_result)
        assert user_password_result
        self.cmd_sender_id = get_docker_containers_id_from_docker_image_name(self.terminal, "cmd-sender")[0]

    def runTest(self):
        volume_ids = []
        for i in range(64):
            cmd = f"""docker exec {self.cmd_sender_id} """ \
                  f"""python -c 'from scripts.disk_infrastructure import create_ramdrive_and_attach_as_ns_to_subsystem; """ \
                  f"""print(create_ramdrive_and_attach_as_ns_to_subsystem("{self.terminal.config.ip_address}", "Malloc{i}", 4, "{NQN}", {SPDK_PORT}))'"""
            volume_ids.append(self.terminal.execute(cmd)[0])
        assert len(TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS) == 64
