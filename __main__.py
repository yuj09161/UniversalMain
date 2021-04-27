import zipfile
import tempfile
import subprocess

from constants import (
    ENCODING, IS_WINDOWS, PROGRAM_DIR, IS_ZIPFILE, ZIPAPP_FILE
)


def _nt_run_cmd(args):
    return subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW, check=False
    )


def _posix_run_cmd(args):
    return subprocess.run(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )


if IS_WINDOWS:
    run_cmd = _nt_run_cmd
else:
    run_cmd = _posix_run_cmd


def main():
    if IS_ZIPFILE:
        with zipfile.ZipFile(ZIPAPP_FILE) as main_zip:
            with main_zip.open('requirements.txt') as requirements_file:
                requirements = requirements_file.read().decode('utf-8')
    else:
        with open(
            PROGRAM_DIR + 'requirements.txt', 'r', encoding='utf-8'
        ) as file:
            requirements = file.read()
    requirements = filter(None, requirements.splitlines())

    installed = run_cmd(['pip', 'list']).stdout.decode(ENCODING)
    to_install = [
        package for package in requirements if not package + ' ' in installed
    ]
    if to_install:
        # get installer
        if IS_ZIPFILE:
            tmp_dir = tempfile.TemporaryDirectory()
            with zipfile.ZipFile(ZIPAPP_FILE) as main_zip:
                main_zip.extract('installer.py', tmp_dir.name)
                for name in main_zip.namelist():
                    if name.startswith('wincurse'):
                        main_zip.extract(name, tmp_dir.name)
            file_path = tmp_dir.name + '/installer.py'
        else:
            file_path = PROGRAM_DIR + 'installer.py'

        # call installer
        code = subprocess.run(
            ['py', file_path, *to_install], check=False
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
