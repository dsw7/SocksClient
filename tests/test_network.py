from os import getcwd, EX_OK, path
from time import sleep
from typing import List
from logging import getLogger
from tempfile import gettempdir
from json import load, dumps
from subprocess import Popen, PIPE, DEVNULL

LOGGER = getLogger(__name__)
NUM_CMD_ATTEMPTS = 20
DELAY_SEC_BETWEEN_CMD = 5

def test_ping(request_docker_containers: List[str]) -> None:

    command = [f'{getcwd()}/SocksClient/main.py']
    command.extend([f'--servers={ip_addr}' for ip_addr in request_docker_containers])
    command.extend(['ping', '--export-to-file'])

    LOGGER.info('Will attempt to run command %i times:', NUM_CMD_ATTEMPTS)
    LOGGER.info(' '.join(command))

    for attempt in range(1, NUM_CMD_ATTEMPTS + 1):

        with Popen(command, stdout=DEVNULL, stderr=PIPE) as process:
            _, stderr = process.communicate()

            if stderr:
                LOGGER.warning('Command returned stderr: "%s"', stderr.decode())

            assert process.returncode == EX_OK

        LOGGER.info('Checking if all containers respond to ping. Attempt %i of %i', attempt, NUM_CMD_ATTEMPTS)
        sleep(DELAY_SEC_BETWEEN_CMD)

        with open(path.join(gettempdir(), 'ping_results.json')) as f:
            containers = load(f)

        if all(containers[ip_addr]['status'] == 'ALIVE' for ip_addr in request_docker_containers):
            LOGGER.info('All containers ended up responding to ping!')
            LOGGER.info('Results file contents: %s', dumps(containers, indent=4))
            break

    else:
        raise AssertionError('One or more containers did not respond to ping command in time!')

def test_sysinfo(request_docker_containers: List[str]) -> None:

    command = [f'{getcwd()}/SocksClient/main.py']
    command.extend([f'--servers={ip_addr}' for ip_addr in request_docker_containers])
    command.extend(['sysinfo', '--export-to-file'])

    LOGGER.info('Will attempt to run command %i times:', NUM_CMD_ATTEMPTS)
    LOGGER.info(' '.join(command))

    for attempt in range(1, NUM_CMD_ATTEMPTS + 1):

        with Popen(command, stdout=DEVNULL, stderr=PIPE) as process:
            _, stderr = process.communicate()

            if stderr:
                LOGGER.warning('Command returned stderr: "%s"', stderr.decode())

            assert process.returncode == EX_OK

        LOGGER.info('Checking if all containers respond to sysinfo. Attempt %i of %i', attempt, NUM_CMD_ATTEMPTS)
        sleep(DELAY_SEC_BETWEEN_CMD)

        with open(path.join(gettempdir(), 'sysinfo_results.json')) as f:
            containers = load(f)

        if all(containers[ip_addr]['status'] == 'ALIVE' for ip_addr in request_docker_containers):
            LOGGER.info('All containers ended up responding to sysinfo!')
            LOGGER.info('Results file contents: %s', dumps(containers, indent=4))
            break

    else:
        raise AssertionError('One or more containers did not respond to sysinfo command in time!')
