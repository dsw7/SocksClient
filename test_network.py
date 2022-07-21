from os import getcwd, EX_OK
from typing import TypeVar
from logging import getLogger
from subprocess import Popen, DEVNULL
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

        LOGGER.info('Setting up Docker containers...')

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

        LOGGER.info('Tearing down Docker containers...')

        for container in self.containers:
            LOGGER.info('Killing container "%s"', container.name)
            container.kill()

    def test_ping(self: T) -> None:

        command = [f'{getcwd()}/SocksClient/main.py']
        command.extend([f'--servers={s}' for s in self.ip_addr])
        command.extend(['ping', '--export-to-file'])

        LOGGER.info('Running command: "%s"', ' '.join(command))

        process = Popen(command, stdout=DEVNULL)
        process.communicate()

        assert process.returncode == EX_OK
