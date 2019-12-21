import q3df


def get_predicted_playerstate():
    return q3df.Py_GetPredictedPlayerstate()


def echo(msg):
    q3df.Py_Cbuf_ExecuteText("echo \"" + msg + "\"\n")


def kill():
    q3df.Py_Cbuf_ExecuteText("kill\n")
