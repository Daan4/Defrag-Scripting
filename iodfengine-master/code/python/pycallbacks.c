#include "pycallbacks.h"

#define PY_SSIZE_T_CLEAN
#include <Python.h>

int initialized = 0;

PyObject *pCALLBACK_MODULE;

void Py_Embed_Initialize(void) {
    if(!initialized) {
        initialized = 1;
        Py_Initialize();
        
        PyObject *pName;
        pName = PyUnicode_DecodeFSDefault("callbacks");
        pCALLBACK_MODULE = PyImport_Import(pName);
        Py_DECREF(pName);
    }
}

void Py_CL_CreateCmd(usercmd_t *cmd) {
    PyObject *pFunc, *pArgs, *pValue;

    pFunc = PyObject_GetAttrString(pCALLBACK_MODULE, "callback");
    pArgs = PyTuple_New(0);
    pValue = PyObject_CallObject(pFunc, pArgs);
    Py_XDECREF(pArgs);
    Py_XDECREF(pValue);
    Py_XDECREF(pFunc);
}
