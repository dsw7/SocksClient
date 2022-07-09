import curses
from concurrent import futures
from core.panel_base import ControlPanelBase
from core.consts import PANEL_MARGIN

HEADER = ' {:<20} {:<20} {:<20}'.format('HOST', 'STATUS', 'UPTIME (HH:MM:SS)')
OFFSET = 21


class PanelPing(ControlPanelBase):

    def run_server_command(self) -> None:
        for server, handle in self.cli_params['clients'].items():
            status = {}

            if not handle.connect():
                status['status'] = 'DEAD'
                status['uptime'] = '-'
                self.results[server] = status
                continue

            status['status'] = 'ALIVE'
            status['uptime'] = handle.send('uptime')

            handle.disconnect()
            self.results[server] = status

    def render_subwin_header(self) -> None:
        frequency = 1 / (self.cli_params['configs']['frontend'].getint('panel_refresh_period_msec') / 1000)

        self.body.addstr(1, PANEL_MARGIN - 1, ' Panel type:')
        self.body.addstr(1, PANEL_MARGIN + 20, 'PING', curses.A_UNDERLINE)
        self.body.addstr(2, PANEL_MARGIN - 1, ' Refresh frequency:')
        self.body.addstr(2, PANEL_MARGIN + 20, '{} Hz'.format(frequency))
        self.body.addstr(4, PANEL_MARGIN - 1, HEADER + ' ' * (self.body.getmaxyx()[1] - len(HEADER) - 4), curses.A_REVERSE)

    def render_body(self) -> None:
        for index, (server, status) in enumerate(self.results.items(), 5):  # Offset to account for header position
            self.body.addstr(index, PANEL_MARGIN + 0 * OFFSET, server)

            # Clears from cursor to EOL - so covers both the following addstr
            self.body.clrtoeol()
            self.body.addstr(index, PANEL_MARGIN + 1 * OFFSET, status['status'])
            self.body.addstr(index, PANEL_MARGIN + 2 * OFFSET, status['uptime'])

    def update_body(self) -> None:
        sleep_msec = self.cli_params['configs']['frontend'].getint('panel_refresh_period_msec')

        while self.run_program:
            self.run_server_command()
            self.render_body()
            self.body.refresh()
            self.stdscr.refresh()
            curses.napms(sleep_msec)

    def main(self) -> None:
        self.display_header()
        self.display_footer()
        self.render_subwin_header()

        with futures.ThreadPoolExecutor() as executor:
            executor.submit(self.update_body)
            executor.submit(self.wait_for_user_input)


# See https://docs.python.org/3/howto/curses.html#starting-and-ending-a-curses-application
def panel_ping(stdscr: curses.window, cli_params: dict) -> None:
    PanelPing(stdscr, cli_params).main()
