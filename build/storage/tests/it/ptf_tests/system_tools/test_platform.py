# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.config import (
    HostTargetConfig,
    IPUStorageConfig,
    StorageTargetConfig,
)
from system_tools.ssh_terminal import SSHTerminal
import time


class BaseTestPlatform:
    """A base class used to represent operating system with needed libraries"""

    def __init__(self, terminal: SSHTerminal):
        self.terminal = terminal
        self.pms = "dnf" if self._is_dnf() else "apt-get" if self._is_apt() else None
        self.system = self._os_system()

    def _os_system(self) -> str:
        return self.terminal.execute("sudo cat /etc/os-release | grep ^ID=")[0][3:]

    def _is_dnf(self) -> bool:
        _, stdout, _ = self.terminal.client.exec_command("dnf --version")
        return not stdout.channel.recv_exit_status()

    def _is_apt(self) -> bool:
        _, stdout, _ = self.terminal.client.exec_command("apt-get --version")
        return not stdout.channel.recv_exit_status()

    def _is_docker(self) -> bool:
        _, stdout, _ = self.terminal.client.exec_command("docker --version")
        return not stdout.channel.recv_exit_status()

    def _is_virtualization(self) -> bool:
        """Checks if VT-x/AMD-v support is enabled in BIOS"""

        expectations = ["vt-x", "amd-v", "full"]
        out = self.terminal.execute("lscpu | grep -i virtualization")[0]
        for allowed_str in expectations:
            if allowed_str.upper() in out.upper():
                return True
        return False

    def _is_kvm(self) -> bool:
        """Checks if kvm modules are loaded"""

        expectations = ["kvm_intel", "kvm_amd"]
        out = self.terminal.execute("lsmod | grep -i kvm")[0]
        for allowed_str in expectations:
            if allowed_str.upper() in out.upper():
                return True
        return False

    # TODO add implementation
    def _is_qemu(self) -> bool:
        return True

    def _install_libguestfs_tools(self) -> bool:
        """Installs libguestfs-tools for a specific OS"""

        program = (
            "libguestfs-tools" if self.system == "ubuntu" else "libguestfs-tools-c"
        )
        out = self.terminal.execute(f"sudo {self.pms} install -y {program}")
        return bool(out)

    def _install_wget(self) -> bool:
        out = self.terminal.execute(f"sudo {self.pms} install -y wget")
        return bool(out)

    def _change_vmlinuz(self) -> bool:
        """Changes the mode of /boot/vmlinuz-*"""

        _, stdout, stderr = self.terminal.client.exec_command(
            "sudo chmod +r /boot/vmlinuz-*"
        )
        return not stdout.read().decode() or stderr.read().decode()

    def _set_security_policies(self) -> bool:
        cmd = (
            "sudo setenforce 0"
            if self.system == "fedora"
            else "sudo systemctl stop apparmor"
        )
        _, stdout, stderr = self.terminal.client.exec_command(cmd)
        return (
            "disabled" in stdout.read().decode() or "disabled" in stderr.read().decode()
        )

    # TODO add implementation
    def _install_docker(self):
        pass

    def check_system_setup(self):
        """Overwrite this method in specific platform if you don't want check all setup"""
        if not self._is_virtualization():
            raise Exception('Virtualization is not setting properly')
        if not self._is_kvm():
            raise Exception('KVM is not setting properly')
        if not self.pms:
            raise Exception('Packet manager is not setting properly')
        if not self._is_qemu():
            raise Exception('QUEMU is not setting properly')
        if not self._set_security_policies():
            raise Exception('Security polices is not setting properly')
        if not self._is_docker():
            raise Exception('Docker is not setting properly')

    # TODO: after testing restore settings
    def set_system_setup(self):
        """Overwrite this method in specific platform if you don't want set all setup"""
        self._change_vmlinuz()
        if not self._is_docker():
            self._install_docker()

    def get_pid_from_port(self, port: int):
        result = self.terminal.execute(f"sudo netstat -anop | grep -Po ':{port}\s.*LISTEN.*?\K\d+(?=/)' || true")
        return result[0] if result else None

    def kill_process_from_port(self, port: int):
        """Raise error if there is no process in specific port"""
        pid = self.get_pid_from_port(port)
        self.terminal.execute(f"sudo kill -9 {pid}")

class StorageTargetPlatform(BaseTestPlatform):

    def __init__(self):
        config = StorageTargetConfig()
        terminal = SSHTerminal(config)
        super().__init__(terminal)

    # TODO add implementation
    def create_subsystem(self):
        pass

    # TODO add implementation
    def create_ramdrive(self):
        return 'Guid'


class IPUStoragePlatform(BaseTestPlatform):

    def __init__(self):
        config = IPUStorageConfig()
        terminal = SSHTerminal(config)
        super().__init__(terminal)

    # TODO add implementation
    def create_virtio_blk_device(self):
        return 'VirtioBlkDevice'


class HostTargetPlatform(BaseTestPlatform):

    def __init__(self):
        config = HostTargetConfig()
        terminal = SSHTerminal(config)
        super().__init__(terminal)

    # TODO add implementation
    def run_fio(self):
        return 'FioOutput'

    # TODO add implementation
    def check_number_of_virtio_blks(self):
        return 'int'


from tenacity import retry, stop_after_delay
import os


class VirtualMachine:

    def __init__(self, platform):
        self.platform = platform
        self.storage_path = os.path.join(self.platform.terminal.config.workdir, "ipdk/build/storage")
        self.share_path = os.path.join(self.platform.terminal.config.workdir, "shared")
        self.socket_path = os.path.join(self.share_path, 'vm_socket')

    def run(self):
        self.delete()
        if self.platform.get_pid_from_port(5555):
            raise Exception('There is process in 5555 port')
        socket_path = os.path.join(self.share_path, 'vm_socket')
        if os.path.exists(socket_path):
            raise Exception('Socket path is not free')
        cmd = f'SHARED_VOLUME={self.share_path} UNIX_SERIAL=vm_socket scripts/vm/run_vm.sh &> /dev/null &'
        self.platform.terminal.execute(f"cd {self.storage_path} && {cmd}")
        self._wait_to_run(5555)

    def delete(self):
        if self.platform.get_pid_from_port(5555):
            self.platform.kill_process_from_port(5555)
        if self.platform.get_pid_from_port(50051):
            self.platform.kill_process_from_port(50051)
        self.platform.terminal.execute(f'cd {self.share_path} && rm -rf $(ls)')

    @retry(stop=stop_after_delay(600), reraise=True)
    def _wait_to_run(self, port):
        socket_path = os.path.join(self.share_path, 'vm_socket')
        time.sleep(30)
        if not self.platform.get_pid_from_port(port) or not os.path.exists(socket_path):
            raise Exception('VM is not running')
