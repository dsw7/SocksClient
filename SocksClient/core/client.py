from time import sleep
from socket import (
    socket,
    AF_INET,
    SOCK_STREAM
)


class Client:

    def __init__(self, host: str, client_configs: dict) -> None:
        self.client_configs = client_configs
        self.host = host
        self.socket = None

    def connect(self) -> bool:
        status = True

        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.settimeout(self.client_configs.getfloat('sock_timeout'))

        port = self.client_configs.getint('tcp_port')

        for _ in range(self.client_configs.getint('max_connection_attempts')):
            try:
                sleep(0.02)
                self.socket.connect((self.host, port))
            except OSError: # socket.timeout error is a subclass of OSError
                continue    # See https://docs.python.org/3/library/socket.html#socket.timeout
            else:
                break
        else:
            status = False

        return status

    def disconnect(self) -> None:
        self.socket.close()

    def send(self, command: str) -> str:
        self.socket.sendall(command.encode())
        buffer_size = self.client_configs.getint('tcp_buffer_size')

        try:
            bytes_recv = self.socket.recv(buffer_size)
        except ConnectionResetError:
            return ''
        return bytes_recv.decode()

    def stop_server(self) -> None:
        command = 'exit'
        self.socket.sendall(command.encode())
