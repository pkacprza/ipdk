import sys

sys.path.append('../')

from python_system_tools.ssh_terminal import SSHTerminal
from python_system_tools.test_platform import StorageTestPlatform, IPUStorageTestPlatform, HostTargetTestPlatform
from ptf import testutils
from ptf.base_tests import BaseTest


class TestRunDockerContainers(BaseTest):

    def setUp(self):
        self.storage_platform = StorageTestPlatform(SSHTerminal("StorageConfig"))
        self.ipu_storage_platform = IPUStorageTestPlatform(SSHTerminal("IPUStorageConfig"))
        self.host_target_platform = HostTargetTestPlatform(SSHTerminal("HostTargetConfig"))

    def runTest(self):
        assert self.storage_platform.run_storage_target_container() == 0
        assert self.ipu_storage_platform.run_ipu_storage_container() == 0
        assert self.host_target_platform.run_host_target_container() == 0
        out, _ = self.storage_platform.terminal.execute("docker ps")
        assert "storage-target" in out
        out, _ = self.ipu_storage_platform.terminal.execute("docker ps")
        assert "ipu-storage-container" in out
        out, _ = self.host_storage_platform.terminal.execute("docker ps")
        assert "host-target" in out
        out, _ = self.storage_platform.terminal.execute("sudo netstat -anop | grep 4420")
        assert "spdk_tgt" in out
        
    def tearDown(self):
        pass
