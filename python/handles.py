import q3df
from structs import playerState_t
import logging


def set_cl_viewangles(pitch, yaw, roll):
    logging.debug(f"{pitch} {yaw} {roll}")
    q3df.Py_UpdateViewangles(pitch, yaw, roll)


def get_predicted_playerstate():
    pps = q3df.Py_GetPredictedPlayerstate()
    if pps is not None:
        pps = playerState_t(*pps)
    return pps


def echo(msg):
    q3df.Py_Cbuf_ExecuteText("echo \"" + msg + "\"\n")


def kill():
    q3df.Py_Cbuf_ExecuteText("kill\n")
