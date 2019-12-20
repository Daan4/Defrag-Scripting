import os
import logging
from structs import *
import sys
import inspect
import scripts

DEBUG_LOG_FILENAME = "logs/output.log"

# List of possible script classes that can be started/stopped via startscript/stopscript console commands
# Built dynamically in CL_InitCGame by inspecting scripts.py
script_instances = []


# unused atm but might as well leave it in
def CL_InitCGame():
    pass


def CL_Init():
    os.makedirs(os.path.dirname(DEBUG_LOG_FILENAME), exist_ok=True)
    logging.basicConfig(filename=DEBUG_LOG_FILENAME, filemode='w', format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

    # Populate script_classes via inspection of scripts.py
    # Add any class which has BaseScript as a base class
    global script_instances
    classes = inspect.getmembers(sys.modules["scripts"], inspect.isclass)
    script_instances = [x[1]() for x in classes if x[1].__bases__[0] in [scripts.BaseScript, scripts.DefaultScript]]
    # Find and Start any default scripts
    default_script_instances = [x[1]() for x in classes if x[1].__bases__[0] is scripts.DefaultScript]
    for default_script in default_script_instances:
        CL_StartScript(default_script.__class__.__name__, "")


def CL_CreateCmd(*args):
    # logging.debug("CL_CreateCmd " + " ".join(map(str, args)))
    cmd = usercmd_t(*args)
    for script in script_instances:
        cmd = script.run(CL_CreateCmd.__name__, cmd)
    return tuple(cmd)


def CL_StartScript(script_class_name, arg):
    logging.debug(f"Starting script \"{script_class_name}\" with arg \"{arg}\"")
    for script in script_instances:
        script.run(CL_StartScript.__name__, script_class_name, arg)


def CL_StopScript(script_class_name):
    logging.debug(f"Stopping script \"{script_class_name}\"")
    for script in script_instances:
        script.run(CL_StopScript.__name__, script_class_name)


def CL_ParseSnapshot(*args):
    # logging.debug("CL_ParseSnapshot " + " ".join(map(str, args)))
    ps = playerstate_t(*args)
    for script in script_instances:
        script.run(CL_ParseSnapshot.__name__, ps)
    return tuple(ps)


if __name__ == "__main__":
    DEBUG_LOG_FILENAME = "../" + DEBUG_LOG_FILENAME
    CL_InitCGame()
    CL_StartScript("usercmdreplay", "test.csv")
    CL_CreateCmd(1, 2, 3, 4, 5, 6, 7, 8, 9)
    CL_ParseSnapshot(1, 2, 3, 4, 5, 6, 7, 8, 9)
