import sys
from os import getcwd
import docker

DOCKER_TAG = 'socks-test'
NETWORK_NAME = 'socks-network'

try:
    client = docker.from_env()
except docker.errors.DockerException as exc:
    sys.exit(f'Cannot connect to docker. Is the service up and running?\nThe exception was: "{exc}"')

client.images.build(path=getcwd(), tag=DOCKER_TAG)

socks_a = client.containers.run(DOCKER_TAG, detach=True, auto_remove=True)
socks_b = client.containers.run(DOCKER_TAG, detach=True, auto_remove=True)
socks_c = client.containers.run(DOCKER_TAG, detach=True, auto_remove=True)

#ipam_pool = docker.types.IPAMPool(subnet='172.30.0.0/16', gateway='172.30.0.1')
#ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

#network = client.networks.create(NETWORK_NAME, driver='bridge', ipam=ipam_config)
network = client.networks.create(NETWORK_NAME)

#network.connect(socks_a, ipv4_address='172.30.1.1')
#network.connect(socks_b, ipv4_address='172.30.1.2')
#network.connect(socks_c, ipv4_address='172.30.1.3')

network.connect(socks_a)
network.connect(socks_b)
network.connect(socks_c)
