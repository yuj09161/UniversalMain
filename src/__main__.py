import json
import zipfile

from universal_main.universal_constants import (
    PROGRAM_DIR, IS_ZIPFILE, ZIPAPP_FILE
)
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
    if splash_text:
        pre_main_name = config['pre_main']
        if pre_main_name:
            pyside6_splash_main(
                config['main_module'], config['main_func'],
                config['requirements'], splash_text, pre_main_name
            )
        else:
            pyside6_splash_main(
                config['main_module'], config['main_func'],
                config['requirements'], splash_text
            )
    else:
        main(
            config['main_module'], config['main_func'], config['requirements']
        )


if __name__ == '__main__':
    run_main()
