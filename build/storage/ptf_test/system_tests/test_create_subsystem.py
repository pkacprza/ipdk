import sys

sys.path.append('../')

from python_system_tools.docker import Docker
from ptf import testutils
from ptf.base_tests import BaseTest
from data import ip_address, user_name, password, nqn, nvme_port, spdk_port

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
