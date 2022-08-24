import sys

sys.path.append('../')

from python_system_tools.docker import Docker
from scripts import socket_functions
from ptf import testutils
from ptf.base_tests import BaseTest
from data import ip_address_proxy, user_name, password, nqn, spdk_port
from python_system_tools.setup_teardown import set_for_test, tear_down_for_test


class TestCreateRamdriveAndAttachAsNsToSubsystem64(BaseTest):

    VOLUME_IDS = []

    def setUp(self):
        set_for_test()
        self.docker_proxy = Docker(address=ip_address_proxy, user=user_name, password=password)
        self.test_driver_id = self.docker_proxy.get_docker_id(docker_image="test-driver")

    def runTest(self):
        for i in range(64):
            cmd = f'python -c \\\"from scripts.disk_infrastructure import create_ramdrive_and_attach_as_ns_to_subsystem; print(create_ramdrive_and_attach_as_ns_to_subsystem(\'{ip_address}\', \'Malloc{i}\', 4, \'{nqn}\', {spdk_port}))\\\"'
            # volume_id, _ = self.proxy_terminal.execute_in_docker(cmd=cmd, container_id=self.test_driver_id, raise_on_error=False)
            volume_id, _ = self.proxy_terminal.execute_method_in_docker(self.test_driver_id, 'disk_infrastructure',
                                                                        'create_ramdrive_and_attach_as_ns_to_subsystem',
                                                                        ip_address_proxy, f'Malloc{i}', 4, nqn, spdk_port)
            TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS.append(volume_id.strip())
        print(TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS)
        assert len(TestCreateRamdriveAndAttachAsNsToSubsystem64.VOLUME_IDS) == 64

    def tearDown(self):
        tear_down_for_test()

