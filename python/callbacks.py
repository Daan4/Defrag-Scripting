import os
import logging
import ctypes
import traceback
import functools
from constants import *

DEBUG_LOG_FILENAME = "logs/output.log"
ERROR_LOG_FILENAME = "logs/errors.log"


# todo decorator breaks pyobject_callobject even with functools.wraps
def ExceptionLogger(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            # todo improve logging message format
            logging.error(repr(e))
            traceback.print_exc()
            ctypes.windll.user32.MessageBoxW(0, "Error in callbacks.py, see logs/errors.log.", "ERROR", 1)
    return inner


#@ExceptionLogger
def CL_InitCGame():
    os.makedirs(os.path.dirname(DEBUG_LOG_FILENAME), exist_ok=True)
    os.makedirs(os.path.dirname(ERROR_LOG_FILENAME), exist_ok=True)
    logging.basicConfig(filename=DEBUG_LOG_FILENAME, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
    logging.basicConfig(filename=ERROR_LOG_FILENAME, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.ERROR)


#@ExceptionLogger
def CL_CreateCmd(server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove):
    logging.debug(f"{server_time} {angles_1} {angles_2} {angles_3} {buttons} {weapon} {forwardmove} {rightmove} {upmove}")
    forwardmove = MOVE_MAX
    return server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove


if __name__ == "__main__":
    ERROR_LOG_FILENAME = "../" + ERROR_LOG_FILENAME
    DEBUG_LOG_FILENAME = "../" + DEBUG_LOG_FILENAME
    CL_InitCGame()
    CL_CreateCmd(0, 0, 0, 0, 0, 0, 0, 0, 0)
