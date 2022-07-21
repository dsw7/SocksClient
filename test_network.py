import sys
from os import getcwd
import docker

DOCKER_TAG = 'socks-test'

try:
    client = docker.from_env()
except docker.errors.DockerException as exc:
    sys.exit(f'Cannot connect to docker. Is the service up and running?\nThe exception was: "{exc}"')

client.images.build(path=getcwd(), tag=DOCKER_TAG)
client.containers.run(DOCKER_TAG, detach=True, auto_remove=True)
