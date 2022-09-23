from ssh_terminal import SSHTerminal


class TestPlatform:
    def __init__(self, terminal: SSHTerminal):
        self.terminal = terminal


class StorageTestPlatform(TestPlatform):
    def run_storage_target_container(self):
        _, rc = self.terminal.execute(
            cmd="AS_DAEMON=true scripts/run_storage_target_container.sh",
            cwd="STORAGE PATH",
        )
        return rc


class IPUStorageTestPlatform(TestPlatform):
    def run_ipu_storage_container(self):
        _, rc = self.ipu_storage_terminal.execute(
            cmd=f"AS_DAEMON=true SHARED_VOLUME={'SHARED VOLUME PATH'} "
            f"scripts/run_ipu_storage_container.sh",
            cwd="STORAGE PATH",
        )
        return rc


class HostTargetTestPlatform(TestPlatform):
    def run_host_target_container(self):
        _, rc = self.storage_terminal.execute(
            cmd="AS_DAEMON=true scripts/run_host_target_container.sh",
            cwd="STORAGE PATH",
        )
        return rc
