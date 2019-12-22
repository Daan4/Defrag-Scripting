import os
import logging
from structs import usercmd_t, playerState_t
import sys
import inspect
import g
from handles import test

# import any files containing scripts.
# the module names should also be in the global constant SCRIPT_MODULES
import scripts
import scripts_record_playback

DEBUG_LOG_FILENAME = "logs/output.log"

SCRIPT_FILES = ["scripts", "scripts_record_playback"]


def getScriptInstances(classes, script_class, start=False):
    """Find and optionally start classes with script_class as their base class"""
    instances = [x[1]() for x in classes if x[1].__bases__[0] == script_class]
    if start:
        for instance in instances:
            instance.CL_StartScript()
    return instances


# unused atm but might as well leave it in
def CL_InitCGame():
    pass


def CL_Init():
    os.makedirs(os.path.dirname(DEBUG_LOG_FILENAME), exist_ok=True)
    logging.basicConfig(filename=DEBUG_LOG_FILENAME, filemode='w', format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

    # Populate script_instances via inspection of python script files
    classes = []
    for file in SCRIPT_FILES:
        classes += inspect.getmembers(sys.modules[file], inspect.isclass)
    # Order of adding to script_instances is the callback execution order
    # Order: StartScript, BotScript, BaseScript, FinalScript
    g.script_instances = []
    g.script_instances += getScriptInstances(classes, scripts.StartScript, True)
    g.script_instances += getScriptInstances(classes, scripts.BotScript)
    g.script_instances += getScriptInstances(classes, scripts.BaseScript)
    g.script_instances += getScriptInstances(classes, scripts.FinalScript, True)

    # run test function for C debugging purposes
    # implement Py_TestFunction in c and the return value will be logged
    # test()


def CL_CreateCmd(*args):
    cmd = usercmd_t(*args)
    for script in g.script_instances:
        cmd = script.run(CL_CreateCmd.__name__, cmd)
    return tuple(cmd)


def CL_StartScript(script_class_name, *args, **kwargs):
    for script in g.script_instances:
        if script.run(CL_StartScript.__name__, script_class_name, lambda: False, *args, **kwargs):
            return script


def CL_StopScript(script_class_name):
    for script in g.script_instances:
        if script.run(CL_StopScript.__name__, script_class_name):
            return script


def CL_ParseSnapshot(*args):
    ps = playerState_t(*args)
    for script in g.script_instances:
        script.run(CL_ParseSnapshot.__name__, ps)


if __name__ == "__main__":
    DEBUG_LOG_FILENAME = "../" + DEBUG_LOG_FILENAME
    CL_InitCGame()
    CL_Init()
    CL_StartScript("nicewalkbot")
    CL_StopScript("nicewalkbot")
    CL_CreateCmd(1, 2, 3, 4, 5, 6, 7, 8, 9)
    CL_ParseSnapshot(*list(range(117)))
