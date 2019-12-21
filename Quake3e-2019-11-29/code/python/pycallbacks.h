#include "../client/client.h"

#define PY_SSIZE_T_CLEAN
#include <Python.h>

// Callback from client/cl_input.c : CL_CreateCmd
void Py_CL_CreateCmd(usercmd_t *cmd);

// Callback from client/cl_cgame.c : CL_InitCGame
void Py_CL_InitCGame(void);

// Callback from client/cl_main.c : CL_Init
void Py_CL_Init(void);

// Callback from client/cl_main.c : CL_ExecScript
void Py_CL_StartScript(char *scriptClassName, char *arg);

// Callback from client/cl_main.c : CL_StopScript
void Py_CL_StopScript(char *scriptClassName);

// Callback from client/cl_parse.c : CL_ParseSnapshot
void Py_CL_ParseSnapshot(clientActive_t *cl);

// Handle to qcommon/qcommon.h : Cbuf_ExecuteText;
PyObject *Py_Cbuf_ExecuteText(PyObject *self, PyObject *args);

PyObject *Py_GetPredictedPlayerstate(PyObject *self, PyObject *args);

// Helper functions
PyObject *usercmdToTuple(usercmd_t *cmd);

void tupleToUsercmd(PyObject *tuple, usercmd_t *cmd);

PyObject *playerStateToTuple(playerState_t *ps);

void tupleToPlayerState(PyObject *tuple, playerState_t *ps);
