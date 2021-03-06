#!/usr/bin/env python3

import sys
from os import path
from typing import Tuple
from curses import wrapper
from configparser import ConfigParser
from click import group, pass_context, pass_obj, option
from core.client import Client

def read_socks_config_file() -> ConfigParser:

    ini_file = path.join(path.dirname(__file__), 'configs', 'socks.ini')

    if not path.exists(ini_file):
        sys.exit(f'Could not open {ini_file}')

    parser = ConfigParser()
    parser.read(ini_file)

    return parser

@group()
@option(
    '-s', '--servers', multiple=True,
    help='Specify one or more socks server IP addresses. This will override values specified in socks.ini',
    metavar='<server-ip-addr>'
)
@pass_context
def main(context, servers: Tuple[str]) -> None:

    context.ensure_object(dict)
    configs = read_socks_config_file()

    context.obj['configs'] = configs
    context.obj['clients'] = {}

    if not servers:
        servers = configs['servers'].values()

    for server in servers:
        context.obj['clients'][server] = Client(client_configs=configs['client-configs'], host=server)

@main.command(help='Open curses panel displaying machine status and uptime')
@option('-f', '--export-to-file', is_flag=True, help='Export results to JSON file')
@pass_obj
def ping(obj, export_to_file: bool) -> None:

    from core.panel_ping import export_results_to_json, panel_ping # Import here to ensure lazy evaluation

    if export_to_file:
        export_results_to_json(obj['clients'])
        return

    wrapper(panel_ping, obj)

@main.command(help='Open curses panel displaying machine uname results')
@option('-f', '--export-to-file', is_flag=True, help='Export results to JSON file')
@pass_obj
def sysinfo(obj, export_to_file: bool) -> None:

    from core.panel_sysinfo import export_results_to_json, panel_sysinfo

    if export_to_file:
        export_results_to_json(obj['clients'])
        return

    wrapper(panel_sysinfo, obj)

if __name__ == '__main__':
    main()
