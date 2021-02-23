import os
import locale
import zipfile
import tempfile
import subprocess


ENCODING = locale.getpreferredencoding()
PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))
LINESEP = os.linesep

# for zipapp support
IS_ZIPFILE = os.path.isfile(PROGRAM_DIR)


def main():
    if IS_ZIPFILE:
        with zipfile.ZipFile(PROGRAM_DIR) as main_zip:
            with main_zip.open('requirements.txt') as requirements_file:
                requirements = requirements_file.read().decode('utf-8')
    else:
        with open(
            PROGRAM_DIR + '/requirements.txt', 'r', encoding='utf-8'
        ) as file:
            requirements = file.read()
    requirements = [
        name
        for name in requirements.replace(LINESEP, '\n').split('\n')
        if name
    ]

    installed = subprocess.run(
        ['pip', 'list'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW, check=False
    )
    to_install = [
        package for i, package in enumerate(requirements)
        if not package + ' ' in installed.stdout.decode(ENCODING)
    ]
    if to_install:
        # get installer
        if IS_ZIPFILE:
            tmp_dir = tempfile.TemporaryDirectory()
            with zipfile.ZipFile(PROGRAM_DIR) as main_zip:
                main_zip.extract('installer.py', tmp_dir.name)
                [  # pylint: disable=expression-not-assigned
                    main_zip.extract(name, tmp_dir.name)
                    for name in main_zip.namelist()
                    if name.startswith('wincurse')
                ]
            file_path = tmp_dir.name + '/installer.py'
        else:
            file_path = PROGRAM_DIR + '/installer.py'

        # call installer
        code = subprocess.run(
            ['py', file_path, *to_install],
            creationflags=subprocess.CREATE_NEW_CONSOLE, check=False
        ).returncode

        if IS_ZIPFILE:
            tmp_dir.cleanup()

        if not code:
            run()
    else:
        run()


# Codes to run
def run():
    # pylint: disable = redefined-outer-name, import-outside-toplevel
    import main  # noqa: E402
    main.main()


if __name__ == '__main__':
    main()
