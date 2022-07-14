import os
import sys
from typing import Tuple

sys.path.append('../')

from python_system_tools.extendedterminal import ExtendedTerminal
from python_system_tools.setup import Setup


class ContainersDeploy:
    """
    A class used to represent a deployment of the storage and proxy containers

    ...

    Attributes
    ----------
    proxy_terminal: ExtendedTerminal
        A session with an SSH server on a proxy target
    storage_terminal: ExtendedTerminal
        A session with an SSH server on a storage target
    workspace_path: str
        A path of the workspace
    repo_path: str
        A path of the repository
    storage_path: str
        A path of the storage
    shared_volume_path: str
        A path of the shared volume

    Methods
    -------
    run_docker_containers()
        Run storage target container and proxy container
    run_vm_instance_on_proxy_container_platform()
        Run VM on a proxy container
    """

    def __init__(
        self, proxy_terminal: ExtendedTerminal, storage_terminal: ExtendedTerminal
    ):
        """
        Parameters
        ----------
        proxy_terminal: ExtendedTerminal
            A session with an SSH server on a proxy target
        storage_terminal: ExtendedTerminal
            A session with an SSH server on a storage target
        """

        self.proxy_terminal = proxy_terminal
        self.storage_terminal = storage_terminal
        self.workspace_path = "/home/berta/IPDK_workspace/"
        self.repo_path = os.path.join(self.workspace_path, "ipdk")
        self.storage_path = os.path.join(
            self.workspace_path,
            "ipdk/build/storage",
        )
        self.shared_volume_path = os.path.join(self.workspace_path, "SHARE")

    def run_docker_containers(self) -> Tuple[int, int]:
        """
        Run storage target container and proxy container

        Returns
        -------
        tuple(int, int)
            A tuple of return codes from running containers
        """

        self.proxy_terminal.mkdir(path=self.shared_volume_path)
        return_values = Setup.setup_on_both_machines(
            # Run on storage-target-platform
            self.storage_terminal.execute_as_root,
            # Run on proxy-container-platform
            self.proxy_terminal.execute_as_root,
            kwargs1={
                "cwd": self.storage_path,
                "cmd": "AS_DAEMON=true scripts/run_storage_target_container.sh",
            },
            kwargs2={
                "cwd": self.storage_path,
                "cmd": f"AS_DAEMON=true SHARED_VOLUME={self.shared_volume_path} scripts/run_proxy_container.sh",
            },
            timeout=900,
        )

        # return_values contains a tuples of output and return code
        return_codes = [element[1] for element in return_values]

        return return_codes

    def run_vm_instance_on_proxy_container_platform(self):
        """Run VM on a proxy container"""

        self.proxy_terminal.execute_as_root(
            cmd=f"cd {self.storage_path} && SHARED_VOLUME={self.shared_volume_path} "
            f"./scripts/vm/run_vm.sh"
        )

    def run_tests(self) -> bool:
        """Run tests on a proxy container and build docker images"""

        _, rc = self.proxy_terminal.execute_as_root(
            cmd="tests/it/run.sh", cwd=self.storage_path
        )
        return not rc