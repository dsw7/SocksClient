from os import getcwd, path
from typing import List
from logging import getLogger
import docker
import pytest

DOCKER_TAG = 'socks-test'
LOGGER = getLogger(__name__)

@pytest.fixture(scope='session')
def request_docker_containers() -> List[str]:

    try:
        client = docker.from_env()
    except docker.errors.DockerException as exc:
        pytest.exit(f'Cannot connect to docker. Is the service up and running?\nThe exception was: "{exc}"')

    client.images.build(path=path.join(getcwd(), 'tests'), tag=DOCKER_TAG)

    LOGGER.info('Setting up Docker containers...')

    containers = [
        client.containers.run(DOCKER_TAG, detach=True, auto_remove=True),
        client.containers.run(DOCKER_TAG, detach=True, auto_remove=True),
        client.containers.run(DOCKER_TAG, detach=True, auto_remove=True)
    ]

    for container in containers:
        LOGGER.info('Running container "%s"', container.name)

    ip_addresses = [
        f'172.17.0.{i}' for i in range(2, len(containers) + 2)  # 172.17.0.0/16 is default subnet for docker
    ]

    yield ip_addresses

    LOGGER.info('Tearing down Docker containers...')

    for container in containers:
        LOGGER.info('Killing container "%s"', container.name)
        container.kill()
