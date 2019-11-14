import os
import logging
from scripts import init_scripts
from structs import *

DEBUG_LOG_FILENAME = "logs/output.log"

callback_observers = None


# Called only once
def CL_InitCGame():
    global callback_observers
    callback_observers = init_scripts()
    os.makedirs(os.path.dirname(DEBUG_LOG_FILENAME), exist_ok=True)
    logging.basicConfig(filename=DEBUG_LOG_FILENAME, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def CL_CreateCmd(*args):
    cmd = usercmd_t(*args)
    for observer in callback_observers:
        cmd = observer.run(CL_CreateCmd.__name__, cmd)
    logging.debug(repr(cmd))
    return tuple(cmd)


if __name__ == "__main__":
    DEBUG_LOG_FILENAME = "../" + DEBUG_LOG_FILENAME
    CL_InitCGame()
    CL_CreateCmd(1, 2, 3, 4, 5, 6, 7, 8, 9)
