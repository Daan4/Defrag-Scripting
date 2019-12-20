#include "pycallbacks.h"

// Python file and function names
const char *CALLBACKS_FILENAME = "callbacks";
const char *CL_INITCGAME_FUNCTION = "CL_InitCGame";
const char *CL_INIT_FUNCTION = "CL_Init";
const char *CL_CREATECMD_FUNCTION = "CL_CreateCmd";
const char *CL_STARTSCRIPT_FUNCTION = "CL_StartScript";
const char *CL_STOPSCRIPT_FUNCTION = "CL_StopScript";
const char *CL_PARSESNAPSHOT_FUNCTION = "CL_ParseSnapshot";

PyObject *CALLBACK_MODULE;

// Expose C functions to python
static PyMethodDef Methods[] = {
    {"Py_Cbuf_ExecuteText", Py_Cbuf_ExecuteText, METH_VARARGS, "Execute a console command."},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef q3dfmodule = {
    PyModuleDef_HEAD_INIT,
    "q3df",
    NULL,
    -1,
    Methods
};

PyMODINIT_FUNC PyInit_q3df(void)
{
    return PyModule_Create(&q3dfmodule);
}

// CALLBACK FUNCTIONS
void Py_CL_InitCGame(void) {
    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_INITCGAME_FUNCTION);
    PyObject_CallObject(Func, NULL);

    Py_DECREF(Func);
}

void Py_CL_Init(void) {
    PyImport_AppendInittab("q3df", PyInit_q3df);

    Py_Initialize();

    PyObject *Name = PyUnicode_DecodeFSDefault(CALLBACKS_FILENAME);
    CALLBACK_MODULE = PyImport_Import(Name);

    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_INIT_FUNCTION);
    PyObject_CallObject(Func, NULL);

    Py_DECREF(Name);
    Py_DECREF(Func);
}

void Py_CL_CreateCmd(usercmd_t *cmd) {
    // Pass usercmd_t struct fields to python and replace cmd with the return values
    PyObject *Args = usercmdToTuple(cmd);

    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_CREATECMD_FUNCTION);
    PyObject *Value = PyObject_CallObject(Func, Args);

    tupleToUsercmd(Value, cmd);

    Py_DECREF(Args);
    Py_DECREF(Func);
    Py_DECREF(Value);
}

void Py_CL_StartScript(char *scriptClassName, char *arg) {
    PyObject *Args = PyTuple_New(2);
    PyTuple_SetItem(Args, 0, PyUnicode_FromString(scriptClassName));
    PyTuple_SetItem(Args, 1, PyUnicode_FromString(arg));

    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_STARTSCRIPT_FUNCTION);
    PyObject_CallObject(Func, Args);

    Py_DECREF(Args);
    Py_DECREF(Func);
}

void Py_CL_StopScript(char *scriptClassName) {
    PyObject *Args = PyTuple_New(1);
    PyTuple_SetItem(Args, 0, PyUnicode_FromString(scriptClassName));

    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_STOPSCRIPT_FUNCTION);
    PyObject_CallObject(Func, Args);

    Py_DECREF(Args);
    Py_DECREF(Func);
}

void Py_CL_ParseSnapshot(clientActive_t *cl) {
//    playerState_t *ps = &(cl->snap.ps);
//
//    PyObject *Args = PyTuple_New(105);
//
//    PyTuple_SetItem(Args, 0, PyLong_FromLong(ps->commandTime));
//    PyTuple_SetItem(Args, 1, PyLong_FromLong(ps->pm_type));
//    PyTuple_SetItem(Args, 2, PyLong_FromLong(ps->bobCycle));
//    PyTuple_SetItem(Args, 3, PyLong_FromLong(ps->pm_flags));
//    PyTuple_SetItem(Args, 4, PyLong_FromLong(ps->pm_time));
//
//    PyTuple_SetItem(Args, 5, PyLong_FromLong(ps->origin[0]));
//    PyTuple_SetItem(Args, 6, PyLong_FromLong(ps->origin[1]));
//    PyTuple_SetItem(Args, 7, PyLong_FromLong(ps->origin[2]));
//    PyTuple_SetItem(Args, 8, PyLong_FromLong(ps->velocity[0]));
//    PyTuple_SetItem(Args, 9, PyLong_FromLong(ps->velocity[1]));
//    PyTuple_SetItem(Args, 10, PyLong_FromLong(ps->velocity[2]));
//    PyTuple_SetItem(Args, 11, PyLong_FromLong(ps->weaponTime));
//    PyTuple_SetItem(Args, 12, PyLong_FromLong(ps->gravity));
//    PyTuple_SetItem(Args, 13, PyLong_FromLong(ps->speed));
//    PyTuple_SetItem(Args, 14, PyLong_FromLong(ps->delta_angles[0]));
//    PyTuple_SetItem(Args, 15, PyLong_FromLong(ps->delta_angles[1]));
//    PyTuple_SetItem(Args, 16, PyLong_FromLong(ps->delta_angles[2]));
//
//    PyTuple_SetItem(Args, 17, PyLong_FromLong(ps->groundEntityNum));
//
//    PyTuple_SetItem(Args, 18, PyLong_FromLong(ps->legsTimer));
//    PyTuple_SetItem(Args, 19, PyLong_FromLong(ps->legsAnim));
//
//    PyTuple_SetItem(Args, 20, PyLong_FromLong(ps->torsoTimer));
//    PyTuple_SetItem(Args, 21, PyLong_FromLong(ps->torsoAnim));
//
//    PyTuple_SetItem(Args, 22, PyLong_FromLong(ps->movementDir));
//
//    PyTuple_SetItem(Args, 23, PyLong_FromLong(ps->grapplePoint[0]));
//    PyTuple_SetItem(Args, 24, PyLong_FromLong(ps->grapplePoint[1]));
//    PyTuple_SetItem(Args, 25, PyLong_FromLong(ps->grapplePoint[2]));
//
//    PyTuple_SetItem(Args, 26, PyLong_FromLong(ps->eFlags));
//
//    PyTuple_SetItem(Args, 28, PyLong_FromLong(ps->eventSequence));
//    PyTuple_SetItem(Args, 27, PyLong_FromLong(ps->events[0]));
//    PyTuple_SetItem(Args, 28, PyLong_FromLong(ps->events[1]));
//    PyTuple_SetItem(Args, 29, PyLong_FromLong(ps->eventParms[0]));
//    PyTuple_SetItem(Args, 30, PyLong_FromLong(ps->eventParms[1]));
//
//    PyTuple_SetItem(Args, 31, PyLong_FromLong(ps->externalEvent));
//    PyTuple_SetItem(Args, 32, PyLong_FromLong(ps->externalEventParm));
//    PyTuple_SetItem(Args, 33, PyLong_FromLong(ps->externalEventTime));
//
//    PyTuple_SetItem(Args, 34, PyLong_FromLong(ps->clientNum));
//    PyTuple_SetItem(Args, 35, PyLong_FromLong(ps->weapon));
//    PyTuple_SetItem(Args, 36, PyLong_FromLong(ps->weaponstate));
//
//    PyTuple_SetItem(Args, 37, PyLong_FromLong(ps->viewangles[0]));
//    PyTuple_SetItem(Args, 38, PyLong_FromLong(ps->viewangles[1]));
//    PyTuple_SetItem(Args, 39, PyLong_FromLong(ps->viewangles[2]));
//    PyTuple_SetItem(Args, 40, PyLong_FromLong(ps->viewheight));
//
//    PyTuple_SetItem(Args, 41, PyLong_FromLong(ps->damageEvent));
//    PyTuple_SetItem(Args, 42, PyLong_FromLong(ps->damageYaw));
//    PyTuple_SetItem(Args, 43, PyLong_FromLong(ps->damagePitch));
//    PyTuple_SetItem(Args, 44, PyLong_FromLong(ps->damageCount));
//
//    int i;
//    for(i = 0; i < 16; i++) {
//        PyTuple_SetItem(Args, 45 + i, PyLong_FromLong(ps->stats[i]));
//        PyTuple_SetItem(Args, 61 + i, PyLong_FromLong(ps->persistant[i]));
//        PyTuple_SetItem(Args, 76 + i, PyLong_FromLong(ps->powerups[i]));
//        PyTuple_SetItem(Args, 82 + i, PyLong_FromLong(ps->ammo[i]));
//    }
//
//    PyTuple_SetItem(Args, 98, PyLong_FromLong(ps->generic1));
//    PyTuple_SetItem(Args, 99, PyLong_FromLong(ps->loopSound));
//    PyTuple_SetItem(Args, 100, PyLong_FromLong(ps->jumppad_ent));
//
//    PyTuple_SetItem(Args, 101, PyLong_FromLong(ps->ping));
//    PyTuple_SetItem(Args, 102, PyLong_FromLong(ps->pmove_framecount));
//    PyTuple_SetItem(Args, 103, PyLong_FromLong(ps->jumppad_frame));
//    PyTuple_SetItem(Args, 104, PyLong_FromLong(ps->entityEventSequence));
//
//    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_PARSESNAPSHOT_FUNCTION);
//    PyObject_CallObject(Func, Args);
//
//    Py_DECREF(Args);
//    Py_DECREF(Func);
}

// FUNCTION HANDLES CALLABLE FROM PYTHON
// Execute console commands
// args:
//          cmd [string]: console command to send. Must end with a newline (\n)
static PyObject *Py_Cbuf_ExecuteText(PyObject *self, PyObject *args)
{
    char *command;
    if(!PyArg_ParseTuple(args, "s", &command))
        return NULL;

    Cbuf_ExecuteText(EXEC_NOW, command);

    Py_RETURN_NONE;
}

// CONVERTER FUNCTIONS
PyObject *usercmdToTuple(usercmd_t *cmd) {
    PyObject *tuple = PyTuple_New(9);
    PyTuple_SetItem(tuple, 0, PyLong_FromLong(cmd->serverTime));
    PyTuple_SetItem(tuple, 1, PyLong_FromLong(cmd->angles[0]));
    PyTuple_SetItem(tuple, 2, PyLong_FromLong(cmd->angles[1]));
    PyTuple_SetItem(tuple, 3, PyLong_FromLong(cmd->angles[2]));
    PyTuple_SetItem(tuple, 4, PyLong_FromLong(cmd->buttons));
    PyTuple_SetItem(tuple, 5, PyLong_FromLong(cmd->weapon));
    PyTuple_SetItem(tuple, 6, PyLong_FromLong(cmd->forwardmove));
    PyTuple_SetItem(tuple, 7, PyLong_FromLong(cmd->rightmove));
    PyTuple_SetItem(tuple, 8, PyLong_FromLong(cmd->upmove));
    return tuple;
}

void tupleToUsercmd(PyObject *tuple, usercmd_t *cmd) {
    PyArg_ParseTuple(tuple, "iiiiiiiii", &(cmd->serverTime),
                                         &(cmd->angles[0]),
                                         &(cmd->angles[1]),
                                         &(cmd->angles[2]),
                                         &(cmd->buttons),
                                         &(cmd->weapon),
                                         &(cmd->forwardmove),
                                         &(cmd->rightmove),
                                         &(cmd->upmove));
}

//PyObject *playerStateToTuple(usercmd_t *ps) {
//}
//
//void *tupleToPlayerState(PyObject *tuple,  playerstate_t *ps) {
//}
