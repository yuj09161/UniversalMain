import os
import sys
import time
import locale
import platform
import subprocess
import importlib.util


DEBUG = False


# check python version
major, minor = sys.version_info[:2]
if (major, minor) < (3, 7):
    print('This program needs python>=3.7')
    input('Press ENTER to exit')
    sys.exit()

# import curses module
if platform.system() == 'Windows':
    SRC_DIR = os.path.dirname(os.path.abspath(__file__)) + '/'

    for module_name in ('_curses', '_curses_panel'):
        module_path = (
            SRC_DIR + 'wincurses/' + module_name + '.cp'
            + str(major) + str(minor) + '-win'
            + ('_amd64' if platform.architecture()[0] == '64bit' else '32')
            + '.pyd'
        )

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    curses = sys.modules['_curses']
    curses.panel = sys.modules['_curses_panel']
else:
    import curses
    import curses.panel

# end init


ENCODING = locale.getpreferredencoding()


class Installer:
    def __init__(self, to_install):
        self.__to_install = to_install
        self.__row = 0
        self.__pg_status = 0
        self.__is_running = lambda: False

    def run(self):
        try:
            screen = curses.initscr()
            curses.noecho()
            curses.cbreak()
            screen.keypad(True)
            curses.start_color()
            return self.__main(screen)
        finally:
            curses.nocbreak()
            screen.keypad(False)
            curses.echo()
            curses.endwin()

            if DEBUG:
                print('stdout')
                print(self.__popen.stdout.read())
                print()
                print('stderr')
                print(self.__popen.stderr.read())
                input('Press ENTER to exit')

    def __main(self, screen):
        # pylint: disable=attribute-defined-outside-init
        height, width = screen.getmaxyx()
        self.__screen = screen.subwin(
            int(height * 0.5), int(width * 0.5),
            int(height * 0.25), int(width * 0.25)
        )
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        self.__screen.bkgd(' ', curses.color_pair(1))

        self.__screen.addstr(1, 2, 'This program needs these packages:')
        self.__screen.addstr(
            2, 2,
            self.__split_text(self.__to_install, self.__screen.getmaxyx()[1])
        )
        self.__screen.addstr(7, 2, 'Install packages? (y/n)')
        self.__screen.refresh()

        key = self.__screen.getkey()
        while True:
            if key == 'y':
                self.__install()
                while self.__is_running():
                    self.__progress()
                    time.sleep(0.25)
                self.__is_running = lambda: False
                return 0
            elif key == 'n':
                return 1
            else:
                self.__screen.addstr(7, 2, 'Wrong input            ')
                self.__screen.addstr(8, 2, 'Install packages? (y/n)')
                key = self.__screen.getkey()

    def __progress(self):
        height, _ = self.__screen.getmaxyx()
        self.__pg_status = (
            0 if self.__pg_status == 3 else self.__pg_status + 1
        )
        self.__screen.addstr(
            height - 2, 2,
            'Installing ' + ('\\', '|', '/', '-')[self.__pg_status]
        )
        self.__screen.refresh()

    def __install(self):
        popen = subprocess.Popen(
            ['pip', 'install', *self.__to_install],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW, encoding=ENCODING
        )
        if DEBUG:
            # pylint: disable=attribute-defined-outside-init
            self.__popen = popen
        self.__is_running = lambda: popen.poll() is None

    def __split_text(self, to_install, width):
        width -= 5
        text = to_install[0]
        line_len = len(to_install[0])
        for name in to_install[1:]:
            length = len(name)
            if line_len + length >= width:
                text += '\n'
                line_len = length
            else:
                text += ' '
                line_len += length
            text += name
        return text


if __name__ == '__main__':
    installer = Installer(sys.argv[1:])
    sys.exit(installer.run())
