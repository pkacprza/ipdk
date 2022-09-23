from ssh_terminal import SSHTerminal


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

    def __init__(self):

        self.storage_terminal = SSHTerminal("CONFIG")
        self.ipu_storage_terminal = SSHTerminal("CONFIG")
        self.host_target_terminal = SSHTerminal("CONFIG")

    def run_docker_containers(self) -> list[int]:
        """
        Run storage target container and proxy container

        Returns
        -------
        list(int)
            A list of return codes from running containers
        """

        # we need storage path (eg. /home/berta/ipdk/build/storage)
        # we need shared volume path (eg. /home/berta/SHARE)
        return_codes = []
        _, rc = self.storage_terminal.execute(cwd=self.storage_path,
                                              cmd="AS_DAEMON=true scripts/run_storage_target_container.sh")
        return_codes.append(rc)
        _, rc = self.ipu_storage_terminal.execute(cwd=self.storage_path,
                                                  cmd=f"AS_DAEMON=true SHARED_VOLUME={self.shared_volume_path} "
                                                  f"scripts/run_ipu_storage_container.sh")
        return_codes.append(rc)
        _, rc = self.storage_terminal.execute(cwd=self.storage_path,
                                              cmd="AS_DAEMON=true scripts/run_host_target_container.sh")
        return_codes.append(rc)
        return return_codes
