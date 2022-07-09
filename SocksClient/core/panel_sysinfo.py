import sys
import curses
from core.panel_base import ControlPanelBase
from core.consts import PANEL_MARGIN

HEADER = ' {:<15} {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}'.format(
    'HOST', 'STATUS', 'SYSTEM', 'NODE', 'RELEASE', 'MACHINE', 'VERSION'
)
OFFSET = 16
EMPTY_RESULTS = {
    'System': '-',
    'Node': '-',
    'Release': '-',
    'Version':  '-',
    'Machine': '-'
}

def split_results(results: str) -> dict:
    splits = {}
    for result in results.split('\n')[:-1]:
        key, value = result.split(': ')
        splits[key] = value
    return splits


class PanelSysInfo(ControlPanelBase):

    def run_server_command(self) -> None:
        for server, handle in self.cli_params['clients'].items():
            status = {}

            if not handle.connect():
                status['status'] = 'DEAD'
                status['results'] = EMPTY_RESULTS
                self.results[server] = status
                continue

            status['status'] = 'ALIVE'
            status['results'] = split_results(handle.send('sysinfo'))

            handle.disconnect()
            self.results[server] = status

    def render_subwin_header(self) -> None:

        self.body.addstr(1, PANEL_MARGIN - 1, ' Panel type:')
        self.body.addstr(1, PANEL_MARGIN + 15, 'SYSINFO', curses.A_UNDERLINE)
        self.body.addstr(4, PANEL_MARGIN - 1, HEADER + ' ' * (self.body.getmaxyx()[1] - len(HEADER) - 4), curses.A_REVERSE)

    def render_body(self) -> None:
        for index, (server, status) in enumerate(self.results.items(), 5):
            self.body.addstr(index, PANEL_MARGIN + 0 * OFFSET, server)
            self.body.addstr(index, PANEL_MARGIN + 1 * OFFSET, status['status'])
            self.body.addstr(index, PANEL_MARGIN + 2 * OFFSET, status['results']['System'])
            self.body.addstr(index, PANEL_MARGIN + 3 * OFFSET, status['results']['Node'])
            self.body.addstr(index, PANEL_MARGIN + 4 * OFFSET, status['results']['Release'])
            self.body.addstr(index, PANEL_MARGIN + 5 * OFFSET, status['results']['Machine'])
            self.body.addstr(index, PANEL_MARGIN + 6 * OFFSET, status['results']['Version'])

    def main(self) -> None:
        status, servers = self.command_does_not_exist('sysinfo')
        if status:
            sys.exit('Command "sysinfo" does not exist on the following servers:\n{}'.format('\n'.join(servers)))

        self.display_header()
        self.display_footer()
        self.render_subwin_header()

        self.run_server_command()
        self.render_body()
        self.body.refresh()
        self.stdscr.refresh()

        self.wait_for_user_input()


def panel_sysinfo(stdscr: curses.window, cli_params: dict) -> None:
    PanelSysInfo(stdscr, cli_params).main()
