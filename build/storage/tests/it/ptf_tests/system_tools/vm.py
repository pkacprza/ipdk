# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

import logging
import os
import re
import socket
import time

from tenacity import retry, stop_after_delay


# todo delete
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


class VirtualMachine:
    def __init__(self, terminal):
        self.terminal = terminal
        self.storage_path = os.path.join(
            self.terminal.config.workdir, "ipdk/build/storage"
        )
        self.share_path = os.path.join(self.terminal.config.workdir, "shared")
        self.socket_path = os.path.join(self.share_path, "vm_socket")

    def run(self, login, password):
        self.delete()
        if self.terminal.platform.get_pid_from_port(5555):
            raise Exception("There is process in 5555 port")
        if os.path.exists(self.socket_path):
            raise Exception("Socket path is not free")
        cmd = f"SHARED_VOLUME={self.share_path} UNIX_SERIAL=vm_socket scripts/vm/run_vm.sh &> /dev/null &"
        self.terminal.execute(f"cd {self.storage_path} && {cmd}")
        self._wait_to_run(5555)
        self._login(login, password)

    def delete(self):
        if self.terminal.platform.get_pid_from_port(5555):
            self.terminal.platform.kill_process_from_port(5555)
        if self.terminal.platform.get_pid_from_port(50051):
            self.terminal.platform.kill_process_from_port(50051)
        self.terminal.platform.terminal.execute(f"cd {self.share_path} && rm -rf $(ls)")

    @retry(stop=stop_after_delay(600), reraise=True)
    def _wait_to_run(self, port):
        socket_path = os.path.join(self.share_path, "vm_socket")
        time.sleep(30)
        if not self.terminal.platform.get_pid_from_port(port) or not os.path.exists(
            socket_path
        ):
            raise Exception("VM is not running")
        time.sleep(120)

    def _login(self, login, password):
        send_command_over_unix_socket(self.socket_path, login, 1)
        send_command_over_unix_socket(self.socket_path, password, 1)

    def get_number_of_virtio_blk_devices(self):
        cmd = "ls -1 /dev"
        out = send_command_over_unix_socket(
            sock=self.socket_path, cmd=cmd, wait_for_secs=1
        )
        return len(re.findall("vd[a-z]+\\b", out))
