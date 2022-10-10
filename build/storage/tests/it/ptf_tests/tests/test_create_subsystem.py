from ptf.base_tests import BaseTest
from test_connection import BaseTerminalMixin
from system_tools.const import NQN, NVME_PORT, SPDK_PORT
from system_tools.ssh_terminal import CommandException

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
