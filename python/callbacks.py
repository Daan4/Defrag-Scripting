import os
import logging
from scripts import init_scripts

DEBUG_LOG_FILENAME = "logs/output.log"

callback_observers = None


# Called only once
def CL_InitCGame():
    global callback_observers
    callback_observers = init_scripts()

    os.makedirs(os.path.dirname(DEBUG_LOG_FILENAME), exist_ok=True)
    logging.basicConfig(filename=DEBUG_LOG_FILENAME, filemode='w', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def CL_CreateCmd(server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove):
    for observer in callback_observers:
        server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove = \
            observer.run(CL_CreateCmd.__name__, server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove)

    logging.debug(f"{server_time} {angles_1} {angles_2} {angles_3} {buttons} {weapon} {forwardmove} {rightmove} {upmove}")
    return server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove

if __name__ == "__main__":
    DEBUG_LOG_FILENAME = "../" + DEBUG_LOG_FILENAME
    CL_InitCGame()
    CL_CreateCmd(0, 0, 0, 0, 0, 0, 0, 0, 0)
