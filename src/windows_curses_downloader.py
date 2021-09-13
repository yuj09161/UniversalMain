import os
import re
import zipfile
from io import BytesIO
from urllib import request


FILE_DIR = os.path.dirname(os.path.abspath(__file__))


def download_curses(dst: str = FILE_DIR):
    """
    Download windows-curses package from pypi.org.

    Args:
        dst (str, optional):
            The directory to download files.
            Defaults to directory of this file.
    """
    with request.urlopen(
        'https://pypi.org/project/windows-curses/#files'
    ) as req:
        raw_data = req.read()
    urls = re.findall(
        # pylint: disable = anomalous-backslash-in-string
        'https://files\.pythonhosted\.org.+?\.whl',  # noqa: W605
        raw_data.decode()
    )

    for url in urls:
        with request.urlopen(url) as req:
            raw_data = req.read()
        with BytesIO(raw_data) as raw_file:
            with zipfile.ZipFile(raw_file) as zip_file:
                infos = zip_file.infolist()
                for info in infos:
                    if info.filename.endswith('.pyd'):
                        zip_file.extract(info, dst)


if __name__ == '__main__':
    download_curses()
