# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from system_tools.config import (HostTargetConfig, IPUStorageConfig,
                                 StorageTargetConfig)
from system_tools.const import NQN, NVME_PORT, SMA_PORT, SPDK_PORT
from system_tools.docker import Docker
from system_tools.ssh_terminal import SSHTerminal
from system_tools.vm import VirtualMachine


class BaseTestPlatform:
    """A base class used to represent operating system with needed libraries"""

    def __init__(self, terminal):
        self.terminal = terminal
        self.pms = "dnf" if self._is_dnf() else "apt-get" if self._is_apt() else None
        self.system = self._os_system()
        self.docker = Docker(terminal)

    def _os_system(self) -> str:
        return self.terminal.execute("sudo cat /etc/os-release | grep ^ID=")[3:]

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
        out = self.terminal.execute("lscpu | grep -i virtualization")
        for allowed_str in expectations:
            if allowed_str.upper() in out.upper():
                return True
        return False

    def _is_kvm(self) -> bool:
        """Checks if kvm modules are loaded"""

        expectations = ["kvm_intel", "kvm_amd"]
        out = self.terminal.execute("lsmod | grep -i kvm")
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
            raise Exception("Virtualization is not setting properly")
        if not self._is_kvm():
            raise Exception("KVM is not setting properly")
        if not self.pms:
            raise Exception("Packet manager is not setting properly")
        if not self._is_qemu():
            raise Exception("QUEMU is not setting properly")
        if not self._set_security_policies():
            raise Exception("Security polices is not setting properly")
        if not self._is_docker():
            raise Exception("Docker is not setting properly")

    # TODO: after testing restore settings
    def set_system_setup(self):
        """Overwrite this method in specific platform if you don't want set all setup"""
        self._change_vmlinuz()
        if not self._is_docker():
            self._install_docker()

    def get_pid_from_port(self, port: int):
        return self.terminal.execute(
            f"sudo netstat -anop | grep -Po ':{port}\s.*LISTEN.*?\K\d+(?=/)' || true"
        )

    def kill_process_from_port(self, port: int):
        """Raise error if there is no process in specific port"""
        pid = self.get_pid_from_port(port)
        self.terminal.execute(f"sudo kill -9 {pid}")


class StorageTargetPlatform(BaseTestPlatform):
    def __init__(self):
        terminal = SSHTerminal(StorageTargetConfig())
        super().__init__(terminal)

    def create_subsystem(self):
        cmd_sender_id = self.docker.get_docker_containers_id_from_docker_image_name(
            "cmd-sender"
        )[0]
        self.terminal.execute(
            f"""docker exec {cmd_sender_id} """
            f"""python -c "from scripts.disk_infrastructure import create_and_expose_subsystem_over_tcp; """
            f"""create_and_expose_subsystem_over_tcp"""
            f"""('{self.terminal.config.ip_address}', '{NQN}', '{NVME_PORT}', {SPDK_PORT})" """
        )

    def create_ramdrive(self, name):
        """Create ramdrive and attach as ns to subsystem"""
        cmd_sender_id = self.docker.get_docker_containers_id_from_docker_image_name(
            "cmd-sender"
        )[0]
        cmd = (
            f"""docker exec {cmd_sender_id} """
            f"""python -c 'from scripts.disk_infrastructure import create_ramdrive_and_attach_as_ns_to_subsystem; """
            f"""print(create_ramdrive_and_attach_as_ns_to_subsystem"""
            f"""("{self.terminal.config.ip_address}", "{name}", 4, "{NQN}", {SPDK_PORT}))'"""
        )
        return self.terminal.execute(cmd)

    def run_storage_target_container(self):
        cmd = (
            f"cd {self.terminal.config.storage_dir} && "
            f"AS_DAEMON=true scripts/run_storage_target_container.sh"
        )
        self.terminal.execute(cmd)
        self.docker.wait_for_running("storage-target")


class IPUStoragePlatform(BaseTestPlatform):
    def __init__(self):
        terminal = SSHTerminal(IPUStorageConfig())
        super().__init__(terminal)

    def create_virtio_blk_device(self, volume_id, physical_id):
        """
        :return: device handle
        """
        cmd_sender_id = self.docker.get_docker_containers_id_from_docker_image_name(
            "cmd-sender"
        )[0]
        cmd = (
            f"""docker exec {cmd_sender_id} """
            f"""python -c "from scripts.disk_infrastructure import create_virtio_blk; """
            f"""print(create_virtio_blk"""
            f"""('{self.terminal.config.ip_address}', '{SMA_PORT}', '{self.terminal.config.ip_address}', 50051, """
            f"""'{volume_id}', '{physical_id}', '0', '{NQN}', """
            f"""'{self.terminal.config.ip_address}', '{NVME_PORT}'))" """
        )
        return self.terminal.execute(cmd)

    def delete_virtio_blk_device(self, device_handle):
        cmd_sender_id = self.docker.get_docker_containers_id_from_docker_image_name(
            "cmd-sender"
        )[0]
        cmd = (
            f"""docker exec {cmd_sender_id} """
            f"""python -c "from scripts.disk_infrastructure import delete_sma_device; """
            f"""print(delete_sma_device"""
            f"""('{self.terminal.config.ip_address}', '{SMA_PORT}', '{self.terminal.config.ip_address}', 50051, '{device_handle}'))" """
        )
        return self.terminal.execute(cmd)

    def run_cmd_sender(self):
        cmd = (
            f"cd {self.terminal.config.storage_dir} && "
            f"AS_DAEMON=true "
            f"scripts/run_cmd_sender.sh"
        )
        self.terminal.execute(cmd)
        self.docker.wait_for_running("cmd-sender")

    def run_ipu_storage_container(self, shared_dir):
        cmd = (
            f"cd {self.terminal.config.storage_dir} && "
            f"AS_DAEMON=true SHARED_VOLUME={shared_dir} "
            f"scripts/run_ipu_storage_container.sh"
        )
        self.terminal.execute(cmd)
        self.docker.wait_for_running("ipu-storage")


class HostTargetPlatform(BaseTestPlatform):
    def __init__(self):
        terminal = SSHTerminal(HostTargetConfig())
        super().__init__(terminal)
        # if vm is not running you have to do it
        self.vm = VirtualMachine(self)

    # TODO add implementation
    def run_fio(self):
        return "FioOutput"

    def run_host_target_container(self):
        cmd = (
            f"cd {self.terminal.config.storage_dir} && "
            f"AS_DAEMON=true scripts/run_host_target_container.sh"
        )
        self.terminal.execute(cmd)
        self.docker.wait_for_running("host-target")
