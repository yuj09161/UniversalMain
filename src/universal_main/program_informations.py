"""Get license, open source notice etc."""

import os
import json
import zipfile
from typing import Union

from .universal_constants import IS_ZIPFILE, ZIPAPP_FILE, PROGRAM_DIR


QPixmap = None
QIcon = None


def _read_file_on_root(relpath: str, encoding: str = 'utf-8')\
        -> Union[str, None]:
    """Read file, stored in program directory or zipfile.

    Args:
        relpath:
            (If not zipapp) Path of file, relative to program root.
            (If zipapp) Path of file in zipapp archive.
        encoding: The encoding of the file to read.
    """
    if IS_ZIPFILE:
        try:
            with zipfile.ZipFile(ZIPAPP_FILE, 'r') as zipapp:
                raw = zipapp.read(relpath)
        except KeyError:
            return None
        else:
            return raw.decode(encoding)
    else:
        try:
            with open(PROGRAM_DIR + relpath, 'r', encoding=encoding) as file:
                contents = file.read()
        except FileNotFoundError:
            pass
        else:
            return contents

        try:
            with open(
                PROGRAM_DIR + '../' + relpath, 'r', encoding=encoding
            ) as file:
                contents = file.read()
        except FileNotFoundError:
            return None
        else:
            return contents


def get_license() -> Union[str, None]:
    """Get license of program.
    It must present on file `LICENSE` (relative to program directory).

    Returns:
        Union[str, None]:
            If file LICENSE is present, return the contents.
            Otherwise, return None.
    """
    return _read_file_on_root('LICENSE')


def get_opensource_notice() -> Union[str, None]:
    """Get license of program.
    It must present on file `NOTICE` (relative to program directory).

    Returns:
        Union[str, None]:
            If file NOTICE is present, return the contents.
            Otherwise, return None.
    """
    return _read_file_on_root('NOTICE')


def get_name() -> Union[str, None]:
    """Get name of program.
    It must present on file `launch.json` (relative to program directory),
    Key `program_name`.

    Returns:
        Union[str, None]:
            If the information is present, return the contents.
            Otherwise, return None.
    """
    info_contents = _read_file_on_root('launch.json')
    if info_contents is None:
        return None
    return json.loads(info_contents)['program_name']


def get_description() -> Union[str, None]:
    """Get license of program.
    It must present on file `programinfo.json` (relative to program directory),
    Key `description`.

    Returns:
        Union[str, None]:
            If the information is present, return the contents.
            Otherwise, return None.
    """
    info_contents = _read_file_on_root('programinfo.json')
    if info_contents is None:
        return None
    return json.loads(info_contents)['description']


def get_license_summary() -> Union[str, None]:
    """Get license summary of program.
    It must present on file `programinfo.json` (relative to program directory),
    Key `license_summary`.

    Returns:
        Union[str, None]:
            If the information is present, return the contents.
            Otherwise, return None.
    """
    info_contents = _read_file_on_root('programinfo.json')
    if info_contents is None:
        return None
    return json.loads(info_contents)['license_summary']


def get_icon() -> Union['QIcon', None]:
    """Get app icon.
    Icon will be loaded from source directory/zipfile.
    Accepted name/type are 'logo.png' and 'logo.jpg'.

    Returns:
        Union[QIcon, None]:
            If PySide6 installed correctly and icon file is present,
            Return the loaded QIcon. Otherwise, return None.
    """
    global QIcon, QPixmap  # pylint: disable = W0602
    if QIcon is None or QPixmap is None:
        try:
            from PySide6.QtGui import QIcon, QPixmap
        except ImportError:
            return None

    if IS_ZIPFILE:
        with zipfile.ZipFile(ZIPAPP_FILE) as main_zip:
            names = main_zip.namelist()
            if 'logo.png' in names:
                data = main_zip.read('logo.png')
            elif 'logo.jpg' in names:
                data = main_zip.read('logo.jpg')
            else:
                return None
    else:
        names = os.listdir(PROGRAM_DIR)
        if 'logo.png' in names:
            with open(PROGRAM_DIR + 'logo.png', 'rb') as file:
                data = file.read()
        elif 'logo.jpg' in names:
            with open(PROGRAM_DIR + 'logo.jpg', 'rb') as file:
                data = file.read()
        else:
            return None

    pixmap = QPixmap()
    pixmap.loadFromData(data)

    return QIcon(pixmap)
