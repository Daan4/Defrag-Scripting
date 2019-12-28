import q3df
from structs import playerState_t
import logging


def set_cl_viewangles(pitch, yaw, roll):
    q3df.Py_UpdateViewangles(pitch, yaw, roll)


def get_predicted_playerstate():
    return playerState_t(*q3df.Py_GetPredictedPlayerstate())


def echo(msg):
    q3df.Py_Cbuf_ExecuteText("echo \"" + msg + "\"\n")


def kill():
    q3df.Py_Cbuf_ExecuteText("kill\n")


def test():
    logging.debug(f"test result {q3df.Py_TestFunction()}")


def console_command(cmd):
    q3df.Py_Cbuf_ExecuteText(f"{cmd}\n")


def set_cvar(name, value):
    q3df.Py_Cvar_Set(name, value)


def get_cvar(name):
    return q3df.Py_Cvar_Get(name)
