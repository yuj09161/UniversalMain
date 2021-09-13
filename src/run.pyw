import os
import subprocess

MAIN_LOCATION = os.path.dirname(os.path.abspath(__file__)) + '/src/__main__.py'
# MAIN_LOCATION = os.path.dirname(os.path.abspath(__file__)) + '/__main__.py'

subprocess.run(
    ['pyw', MAIN_LOCATION],
    creationflags=subprocess.CREATE_NO_WINDOW,
    check=False
)
