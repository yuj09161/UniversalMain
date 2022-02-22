#!/usr/bin/env python3

import json
import zipfile

from universal_main.universal_constants import\
    PROGRAM_DIR, IS_ZIPFILE, ZIPAPP_FILE
from universal_main.universal_main import main, pyside6_splash_main


def run_main():
    """Load startup configuration from file.
    """
    if IS_ZIPFILE:
        with zipfile.ZipFile(ZIPAPP_FILE) as main_zip:
            with main_zip.open('launch.json', 'r') as splash_file:
                config = json.load(splash_file)
    else:
        with open(
            PROGRAM_DIR + 'launch.json', 'r', encoding='utf-8'
        ) as file:
            config = json.load(file)
    splash_text = config['splash']
    if splash_text is None:
        main(
            config['main_module'], config['main_func'],
            config['min_py_ver'], config['requirements']
        )
    else:
        pre_main_name = config['pre_main']
        pyside6_splash_main(
            config['main_module'], config['main_func'],
            config['min_py_ver'], config['requirements'], splash_text,
            '' if pre_main_name is None else pre_main_name
        )


if __name__ == '__main__':
    run_main()
