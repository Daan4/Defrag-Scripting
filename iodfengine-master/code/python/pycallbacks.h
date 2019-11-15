#include "../client/client.h"

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
