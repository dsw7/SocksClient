#!/usr/bin/env python3

import sys
from os import path
from curses import wrapper
from configparser import ConfigParser
from click import (
    group,
    pass_context,
    pass_obj
)
from core.client import Client

def read_socks_config_file() -> ConfigParser:
    ini_file = path.join(path.dirname(__file__), 'configs', 'socks.ini')
    if not path.exists(ini_file):
        sys.exit('Could not open {}'.format(ini_file))

    parser = ConfigParser()
    parser.read(ini_file)
    return parser

@group()
@pass_context
def main(context) -> None:
    context.ensure_object(dict)
    configs = read_socks_config_file()

    context.obj['configs'] = configs
    context.obj['clients'] = {}

    for server in configs['servers'].values():
        context.obj['clients'][server] = Client(client_configs=configs['client-configs'], host=server)

@main.command(help='Open curses panel displaying machine status and uptime')
@pass_obj
def ping(obj) -> None:
    from core.panel_ping import panel_ping  # Import here to ensure lazy evaluation
    wrapper(panel_ping, obj)

@main.command(help='Open curses panel displaying machine uname results')
@pass_obj
def sysinfo(obj) -> None:
    from core.panel_sysinfo import panel_sysinfo
    wrapper(panel_sysinfo, obj)

if __name__ == '__main__':
    main()
