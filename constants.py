import os
import sys
import locale
from multiprocessing import cpu_count


# system settings & information
ENCODING = locale.getpreferredencoding()
LINESEP = os.linesep
PATHSEP = os.path.sep
USER_DIR = os.path.expanduser('~') + PATHSEP
CPU_CNT = cpu_count()
PLATFORM = sys.platform
if PLATFORM == 'win32':
    IS_WINDOWS = True
    DATADIR = os.environ['localappdata'] + PATHSEP
elif PLATFORM == 'linux':
    IS_WINDOWS = False
    DATADIR = USER_DIR + '/.local/share/'
elif PLATFORM == 'darwin':
    IS_WINDOWS = False
    DATADIR = USER_DIR + '/Library/Application Support/'

# runtime info
PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))
IS_ZIPFILE = os.path.isfile(PROGRAM_DIR)
if IS_ZIPFILE:
    ZIPAPP_FILE = PROGRAM_DIR
    while not os.path.isdir(PROGRAM_DIR):
        PROGRAM_DIR = os.path.dirname(os.path.abspath(PROGRAM_DIR))
else:
    ZIPAPP_FILE = ''
PROGRAM_DIR += PATHSEP
