#include "pycallbacks.h"

#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Python file and function names
const char *CALLBACKS_FILENAME = "callbacks";
const char *CL_INITCGAME_FUNCTION = "CL_InitCGame";
const char *CL_CREATECMD_FUNCTION = "CL_CreateCmd";

int initialized = 0;
PyObject *CALLBACK_MODULE;

void Py_CL_InitCGame(void) {
    if(!initialized) {
        initialized = 1;
        Py_Initialize();
        
        PyObject *Name = PyUnicode_DecodeFSDefault(CALLBACKS_FILENAME);
        CALLBACK_MODULE = PyImport_Import(Name);
        
        PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_INITCGAME_FUNCTION);
        PyObject_CallObject(Func, NULL);

        Py_DECREF(Name);
        Py_DECREF(Func);
    }
}

void Py_CL_CreateCmd(usercmd_t *cmd) {
    // Pass usercmd_t struct values to the python callback function
    PyObject *Args = PyTuple_New(9);
    PyTuple_SetItem(Args, 0, PyLong_FromLong(cmd->serverTime));
    PyTuple_SetItem(Args, 1, PyLong_FromLong(cmd->angles[0]));
    PyTuple_SetItem(Args, 2, PyLong_FromLong(cmd->angles[1]));
    PyTuple_SetItem(Args, 3, PyLong_FromLong(cmd->angles[2]));
    PyTuple_SetItem(Args, 4, PyLong_FromLong(cmd->buttons));
    PyTuple_SetItem(Args, 5, PyLong_FromLong(cmd->weapon));
    PyTuple_SetItem(Args, 6, PyLong_FromLong(cmd->forwardmove));
    PyTuple_SetItem(Args, 7, PyLong_FromLong(cmd->rightmove));
    PyTuple_SetItem(Args, 8, PyLong_FromLong(cmd->upmove));

    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_CREATECMD_FUNCTION);

    PyObject *Value = PyObject_CallObject(Func, Args);

    // Replace values in the usercmt_t struct with the returned values
    PyArg_ParseTuple(Value, "iiiiiiiii", &(cmd->serverTime),
                                         &(cmd->angles[0]),
                                         &(cmd->angles[1]),
                                         &(cmd->angles[2]),
                                         &(cmd->buttons),
                                         &(cmd->weapon),
                                         &(cmd->forwardmove),
                                         &(cmd->rightmove),
                                         &(cmd->upmove));
    Py_DECREF(Args);
    Py_DECREF(Func);
    Py_DECREF(Value);
}
