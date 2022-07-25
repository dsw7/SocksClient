from os import getcwd, EX_OK, path
from time import sleep
from typing import TypeVar
from logging import getLogger
from tempfile import gettempdir
from json import load
from subprocess import Popen, PIPE, DEVNULL
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

        client.images.build(path=path.join(getcwd(), 'tests'), tag=DOCKER_TAG)

        LOGGER.info('Setting up Docker containers...')

        self.containers = [
            client.containers.run(DOCKER_TAG, detach=True, auto_remove=True),
            client.containers.run(DOCKER_TAG, detach=True, auto_remove=True),
            client.containers.run(DOCKER_TAG, detach=True, auto_remove=True)
        ]

        for container in self.containers:
            LOGGER.info('Running container "%s"', container.name)

        self.ip_addresses = [
            f'172.17.0.{i}' for i in range(2, len(self.containers) + 2)  # 172.17.0.0/16 is default subnet for docker
        ]

    def teardown_class(self: T) -> None:

        LOGGER.info('Tearing down Docker containers...')

        for container in self.containers:
            LOGGER.info('Killing container "%s"', container.name)
            container.kill()

    def test_ping(self: T) -> None:

        command = [f'{getcwd()}/SocksClient/main.py']
        command.extend([f'--servers={s}' for s in self.ip_addresses])
        command.extend(['ping', '--export-to-file'])

        number_attempts = 20
        LOGGER.info('Will attempt to run command "%s" %i times', ' '.join(command), number_attempts)

        for attempt in range(1, number_attempts + 1):

            with Popen(command, stdout=DEVNULL, stderr=PIPE) as process:
                _, stderr = process.communicate()

                if stderr:
                    LOGGER.warning('Command returned stderr: "%s"', stderr.decode())

                assert process.returncode == EX_OK

            LOGGER.info('Checking if all containers respond to ping. Attempt %i of %i', attempt, number_attempts)
            sleep(5)

            with open(path.join(gettempdir(), 'ping_results.json')) as f:
                containers = load(f)

            if all(containers[ip_addr]['status'] == 'ALIVE' for ip_addr in self.ip_addresses):
                LOGGER.info('All containers ended up responding to ping!')
                break

        else:
            raise AssertionError('One or more containers did not respond to ping command in time!')
