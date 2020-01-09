import os
import logging
from structs import usercmd_t, playerState_t
import sys
import inspect
import g
from helpers import log_exceptions, pause
import threading

# import any files containing scripts.
# the module names should also be in the global constant SCRIPT_MODULES
import scripts_base_classes
import scripts_start
import scripts_bot
import scripts_basic
import scripts_final
import scripts_record_playback

DEBUG_LOG_FILENAME = "logs/output.log"

SCRIPT_FILES = ["scripts_base_classes",
                "scripts_start",
                "scripts_bot",
                "scripts_basic",
                "scripts_final",
                "scripts_record_playback"]


def getScriptInstances(classes, script_class, start=False):
    """Find and optionally start classes with script_class as their base class, except for base classes"""
    instances = [x[1]() for x in classes if x[1].__bases__[0] == script_class and
                 x[1].__name__ not in [scripts_base_classes.StartScript.__name__,
                                       scripts_base_classes.BotScript.__name__,
                                       scripts_base_classes.BasicScript.__name__,
                                       scripts_base_classes.FinalScript.__name__]]

    for instance in instances:
        if instance.autostart:
            instance.CL_StartScript()
    return instances


# unused atm but might as well leave it in
@log_exceptions
def CL_InitCGame():
    pass


@log_exceptions
def CL_Init():
    os.makedirs(os.path.dirname(DEBUG_LOG_FILENAME), exist_ok=True)
    logging.basicConfig(filename=DEBUG_LOG_FILENAME, filemode='w', format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', level=logging.DEBUG, datefmt="%Y-%m-%d %H:%M:%S")

    # Populate script_instances via inspection of python script files
    classes = []
    for file in SCRIPT_FILES:
        classes += inspect.getmembers(sys.modules[file], inspect.isclass)
    # Order of adding to script_instances is the callback execution order
    # Order: StartScript, BotScript, BasicScript, FinalScript
    g.script_instances = []
    g.script_instances += getScriptInstances(classes, scripts_base_classes.StartScript)
    g.script_instances += getScriptInstances(classes, scripts_base_classes.BotScript)
    g.script_instances += getScriptInstances(classes, scripts_base_classes.BasicScript)
    g.script_instances += getScriptInstances(classes, scripts_base_classes.FinalScript)

    # run test function for C debugging purposes
    # implement Py_TestFunction in c and the return value will be logged
    # test()


@log_exceptions
def CL_CreateCmd(*args):
    cmd = usercmd_t(*args)
    for script in g.script_instances:
        cmd = script.run(CL_CreateCmd.__name__, cmd)
    return tuple(cmd)


@log_exceptions
def CL_StartScript(script_class_name, *args, **kwargs):
    for script in g.script_instances:
        if script.run(CL_StartScript.__name__, script_class_name, None, *args, **kwargs) == True:
            return script


@log_exceptions
def CL_StopScript(script_class_name):
    for script in g.script_instances:
        if script.run(CL_StopScript.__name__, script_class_name) == True:
            return script


@log_exceptions
def CL_ParseSnapshot(*args):
    ps = playerState_t(*args)
    for script in g.script_instances:
        script.run(CL_ParseSnapshot.__name__, ps)


@log_exceptions
def CL_LogMessage(message):
    logging.debug(f"C logging: {message}")
