from q3df import Py_Cbuf_ExecuteText


# Echo text to console
def echo(msg):
    Py_Cbuf_ExecuteText("echo \"" + msg + "\"\n")


def kill():
    Py_Cbuf_ExecuteText("kill\n")
