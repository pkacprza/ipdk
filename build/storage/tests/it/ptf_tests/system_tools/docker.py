# Copyright (C) 2022 Intel Corporation
# SPDX-License-Identifier: Apache-2.0
#

from tenacity import retry, stop_after_delay


class Docker:
    def __init__(self, terminal):
        self.terminal = terminal

    def get_docker_containers_id_from_docker_image_name(self, docker_image_name):
        out = self.terminal.execute(
            f'sudo docker ps | grep "{docker_image_name}"'
        ).splitlines()
        return [line.split()[0] for line in out]

    # TODO: add tracking running containers while testing and kill only relevant ones
    def delete_all_containers(self):
        """Delete all containers even currently running"""
        out = self.terminal.execute("docker ps -aq")
        if out:
            self.terminal.execute("docker container rm -fv $(docker ps -aq)")

    @retry(stop=stop_after_delay(180), reraise=True)
    def wait_for_running(self, image_name):
        out = self.terminal.execute("docker ps")
        if image_name not in out:
            raise Exception("Container is not running")
