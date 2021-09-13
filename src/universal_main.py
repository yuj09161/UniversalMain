"""The package install automation tool.
"""

from PySide6.QtWidgets import QSplashScreen

import os
import sys
import shutil
import zipfile
import tempfile
import subprocess
from urllib import request
from urllib.error import URLError
from typing import Iterable, Callable, List

from constants import (
    ENCODING, IS_WINDOWS, PROGRAM_DIR, IS_ZIPFILE, ZIPAPP_FILE
)
from windows_curses_downloader import download_curses


Qt = None
QIcon = None
QApplication = None
QVBoxLayout = None
QLabel = None


def _check_py37() -> bool:
    """
    Check Python version is >= 3.7.

    Returns:
        bool: If version < 3.7, return True. Otherwise, return False.
    """
    if sys.version_info < (3, 7):
        print(
            'This program needs Python >= 3.7.',
            'Please upgrade Python version and try again.',
            sep='\n'
        )
        return True
    return False


class _Splash(QSplashScreen):
    def __init__(self, app, splash_text):
        # pylint: disable = not-callable
        super().__init__()
        x, y = app.screens()[0].availableGeometry().size().toTuple()
        self.setGeometry(x // 2 - 200, y // 2 - 100, 400, 300)
        self.setFixedSize(400, 200)

        self.vl = QVBoxLayout(self)

        self.lb = QLabel(self)
        self.lb.setAlignment(Qt.AlignCenter)
        self.lb.setText(splash_text)
        self.lb.setStyleSheet("font-size: 30px")
        self.vl.addWidget(self.lb)


def _nt_run_cmd(args: List[str]) -> subprocess.CompletedProcess:
    """
    Call subprocess.run with given args.

    Call subprocess.run
    with stdout/stderr PIPE redirect
    and CREATE_NO_WINDOW flag.

    Args:
        args (List[str]): The command to run.

    Returns:
        subprocess.CompletedProcess: The ran result.
    """
    return subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW, check=False
    )


def _posix_run_cmd(args: List[str]) -> subprocess.CompletedProcess:
    """
    Call subprocess.run with given args.

    Call subprocess.run with stdout/stderr PIPE redirect.

    Args:
        args (List[str]): The command to run.

    Returns:
        subprocess.CompletedProcess: The ran result.
    """
    return subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )


if IS_WINDOWS:
    run_cmd = _nt_run_cmd
else:
    run_cmd = _posix_run_cmd


def _check_to_install(requirements: Iterable[str]) -> List[str]:
    """
    Check which packages need to be installed.

    Args:
        requirements (Iterable[str]):
            The pypi package names that must be installed.

    Returns:
        List[str]: The package names.
    """
    installed = run_cmd(['pip', 'list']).stdout.decode(ENCODING)
    return [
        package for package in requirements
        if not package + ' ' in installed
    ]


def _check_network() -> bool:
    """
    Check network is connected.

    Returns:
        bool: If network is unconnected, return True. Otherwise, return False.
    """
    try:
        with request.urlopen('https://example.com', timeout=3):
            pass
    except URLError:
        print(
            'Network is currently unstable.',
            'Please check network connection and try again.',
            sep='\n'
        )
        return True
    return False


def _zipapp_package_installer() -> int:
    """
    The package checker and installer (Python zipapp version.)

    Returns:
        int: The return code from popened process.
    """
    with zipfile.ZipFile(ZIPAPP_FILE) as main_zip:
        with main_zip.open('requirements.txt', 'r') as requirements_file:
            requirements = requirements_file.read().decode('utf-8')
        to_install = _check_to_install(filter(None, requirements.splitlines()))

        if not to_install:
            return 0

        with tempfile.TemporaryDirectory() as tmp_dir:
            main_zip.extract('installer.py', tmp_dir)

            if IS_WINDOWS:
                if _check_network():
                    return 1
                curses_dir = tmp_dir + '/wincurses'
                os.mkdir(curses_dir)
                download_curses(curses_dir)

            return subprocess.run([
                'py', tmp_dir + '/installer.py', *to_install
            ], check=False).returncode


def _normal_package_checker() -> int:
    """
    The package checker and installer (non-zipapp version.)

    Returns:
        int: The return code from popened process.
    """
    with open(
        PROGRAM_DIR + 'requirements.txt', 'r', encoding='utf-8'
    ) as file:
        requirements = file.read()
    to_install = _check_to_install(filter(None, requirements.splitlines()))

    if not to_install:
        return 0

    if IS_WINDOWS:
        with tempfile.TemporaryDirectory() as tmp_dir:
            shutil.copy(PROGRAM_DIR + 'installer.py', tmp_dir)

            if _check_network():
                return 1
            curses_dir = tmp_dir + '/wincurses'
            os.mkdir(curses_dir)
            download_curses(curses_dir)

            return subprocess.run([
                'py', tmp_dir + '/installer.py', *to_install
            ], check=False).returncode

    return subprocess.run(
        ['py', PROGRAM_DIR + 'installer.py', *to_install], check=False
    ).returncode


def main(main_func: Callable):
    """
    The decorator that provide package checker & installer

    Args:
        main_func (Callable):
            The main function.
            It will be called by this function
            if installer successfully executed.
    """
    def inner():
        if _check_py37():
            return

        if IS_ZIPFILE:
            return_code = _zipapp_package_installer()
        else:
            return_code = _normal_package_checker()

        if return_code == 0:
            main_func()
    return inner


def _splash_text_getter() -> str:
    """
    Read text to display at splash screen at splash.txt.

    Returns:
        str:
            The text to display.
            If the file does not exist, return 'No splash.txt'
    """
    try:
        if IS_ZIPFILE:
            with zipfile.ZipFile(ZIPAPP_FILE) as main_zip:
                with main_zip.open('splash.txt', 'r') as splash_file:
                    return splash_file.read().decode('utf-8')
        else:
            with open(
                PROGRAM_DIR + 'splash.txt', 'r', encoding='utf-8'
            ) as file:
                return file.read()
    except (FileNotFoundError, KeyError):
        return 'No splash.txt'


def _check_imports() -> bool:
    """
    Import some PySide6 classes if the classes not imported.

    Will import these classes:
    PySide6.QtCore.Qt
    PySide6.QtGui.QIcon
    PySide6.QtWidgets.QApplication
    PySide6.QtWidgets.QVBoxLayout
    PySide6.QtWidgets.QLabel

    Returns:
        bool: If import failed, return True. Otherwise, return False.
    """
    try:
        # pylint: disable = global-statement
        global Qt
        global QIcon
        global QApplication
        global QVBoxLayout
        global QLabel
        if Qt is None:
            # pylint: disable = redefined-outer-name
            # pylint: disable = import-outside-toplevel
            from PySide6.QtCore import Qt
        if QIcon is None:
            # pylint: disable = redefined-outer-name
            # pylint: disable = import-outside-toplevel
            from PySide6.QtGui import QIcon
        if QApplication is None:
            # pylint: disable = redefined-outer-name
            # pylint: disable = import-outside-toplevel
            from PySide6.QtWidgets import QApplication
        if QVBoxLayout is None:
            # pylint: disable = redefined-outer-name
            # pylint: disable = import-outside-toplevel
            from PySide6.QtWidgets import QVBoxLayout
        if QLabel is None:
            # pylint: disable = redefined-outer-name
            # pylint: disable = import-outside-toplevel
            from PySide6.QtWidgets import QLabel
    except ImportError:
        return True
    return False


def pyside6_splash_main(main_func: Callable):
    """
    The decorator that provide package checker, installer & PySide6 splash.

    Text of splash screen is read from splash.txt at root directory.

    Args:
        main_func (Callable):
            The main function.
            It will be called by this function
            if installer successfully executed.
    """
    def inner():
        if _check_py37():
            return

        # pylint: disable = not-callable
        if _check_imports():  # When PySide6 is not installed
            # Check missing packages and install (with PySide6)
            if IS_ZIPFILE:
                return_code = _zipapp_package_installer()
            else:
                return_code = _normal_package_checker()

            # Create Qt application & Show splash
            app = QApplication()
            app.setWindowIcon(QIcon(PROGRAM_DIR + 'logo.png'))

            splash = _Splash(app, _splash_text_getter())
            splash.show()

        else:  # When PySide6 is installed
            # Create Qt application & Show splash
            app = QApplication()
            app.setWindowIcon(QIcon(PROGRAM_DIR + 'logo.png'))

            splash = _Splash(app, _splash_text_getter())
            splash.show()

            # Check another missing packages
            if IS_ZIPFILE:
                return_code = _zipapp_package_installer()
            else:
                return_code = _normal_package_checker()

        # hide splash
        splash.hide()

        if return_code == 0:
            main_func()
    return inner
