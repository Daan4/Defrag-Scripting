import q3df
from structs import playerState_t


def set_cl_viewangles(pitch, yaw, roll):
    q3df.Py_UpdateViewangles(pitch, yaw, roll)


def get_predicted_playerstate():
    return playerState_t(*q3df.Py_GetPredictedPlayerstate())


def echo(msg):
    q3df.Py_Cbuf_ExecuteText("echo \"" + msg + "\"\n")


def kill():
    q3df.Py_Cbuf_ExecuteText("kill\n")
