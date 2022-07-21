from os import getcwd
from typing import TypeVar
from logging import getLogger
import docker
import pytest

T = TypeVar('T')
DOCKER_TAG = 'socks-test'
LOGGER = getLogger(__name__)


class TestClient:

    def setup_class(self: T) -> None:

        try:
            client = docker.from_env()
        except docker.errors.DockerException as exc:
            pytest.exit(f'Cannot connect to docker. Is the service up and running?\nThe exception was: "{exc}"')

        client.images.build(path=getcwd(), tag=DOCKER_TAG)

        self.containers = [
            client.containers.run(DOCKER_TAG, detach=True, auto_remove=True),
            client.containers.run(DOCKER_TAG, detach=True, auto_remove=True),
            client.containers.run(DOCKER_TAG, detach=True, auto_remove=True)
        ]

        for container in self.containers:
            LOGGER.info('Running container "%s"', container.name)

        self.ip_addr = [
            f'172.17.0.{i}' for i in range(2, len(self.containers) + 2)  # 172.17.0.0/16 is default subnet for docker
        ]

    def teardown_class(self: T) -> None:

        for container in self.containers:
            LOGGER.info('Killing container "%s"', container.name)
            container.kill()

    def test_netcat(self: T) -> None:
        print(self.ip_addr)
