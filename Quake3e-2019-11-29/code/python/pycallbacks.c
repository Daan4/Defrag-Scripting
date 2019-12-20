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
    playerState_t *ps = &(cl->snap.ps);

    PyObject *Args = playerStateToTuple(ps);

    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_PARSESNAPSHOT_FUNCTION);
    PyObject *Value = PyObject_CallObject(Func, Args);

    //tupleToPlayerState(Value, ps);

    Py_DECREF(Args);
    Py_DECREF(Func);
    Py_DECREF(Value);
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

PyObject *playerStateToTuple(playerState_t *ps) {
    PyObject *tuple = PyTuple_New(117);
    PyTuple_SetItem(tuple, 0, PyLong_FromLong(ps->commandTime));
    PyTuple_SetItem(tuple, 1, PyLong_FromLong(ps->pm_type));
    PyTuple_SetItem(tuple, 2, PyLong_FromLong(ps->bobCycle));
    PyTuple_SetItem(tuple, 3, PyLong_FromLong(ps->pm_flags));
    PyTuple_SetItem(tuple, 4, PyLong_FromLong(ps->pm_time));

    PyTuple_SetItem(tuple, 5, PyFloat_FromDouble(ps->origin[0]));
    PyTuple_SetItem(tuple, 6, PyFloat_FromDouble(ps->origin[1]));
    PyTuple_SetItem(tuple, 7, PyFloat_FromDouble(ps->origin[2]));
    PyTuple_SetItem(tuple, 8, PyFloat_FromDouble(ps->velocity[0]));
    PyTuple_SetItem(tuple, 9, PyFloat_FromDouble(ps->velocity[1]));
    PyTuple_SetItem(tuple, 10, PyFloat_FromDouble(ps->velocity[2]));
    PyTuple_SetItem(tuple, 11, PyLong_FromLong(ps->weaponTime));
    PyTuple_SetItem(tuple, 12, PyLong_FromLong(ps->gravity));
    PyTuple_SetItem(tuple, 13, PyLong_FromLong(ps->speed));
    PyTuple_SetItem(tuple, 14, PyLong_FromLong(ps->delta_angles[0]));
    PyTuple_SetItem(tuple, 15, PyLong_FromLong(ps->delta_angles[1]));
    PyTuple_SetItem(tuple, 16, PyLong_FromLong(ps->delta_angles[2]));

    PyTuple_SetItem(tuple, 17, PyLong_FromLong(ps->groundEntityNum));

    PyTuple_SetItem(tuple, 18, PyLong_FromLong(ps->legsTimer));
    PyTuple_SetItem(tuple, 19, PyLong_FromLong(ps->legsAnim));

    PyTuple_SetItem(tuple, 20, PyLong_FromLong(ps->torsoTimer));
    PyTuple_SetItem(tuple, 21, PyLong_FromLong(ps->torsoAnim));

    PyTuple_SetItem(tuple, 22, PyLong_FromLong(ps->movementDir));

    PyTuple_SetItem(tuple, 23, PyFloat_FromDouble(ps->grapplePoint[0]));
    PyTuple_SetItem(tuple, 24, PyFloat_FromDouble(ps->grapplePoint[1]));
    PyTuple_SetItem(tuple, 25, PyFloat_FromDouble(ps->grapplePoint[2]));

    PyTuple_SetItem(tuple, 26, PyLong_FromLong(ps->eFlags));

    PyTuple_SetItem(tuple, 27, PyLong_FromLong(ps->eventSequence));
    PyTuple_SetItem(tuple, 28, PyLong_FromLong(ps->events[0]));
    PyTuple_SetItem(tuple, 29, PyLong_FromLong(ps->events[1]));
    PyTuple_SetItem(tuple, 30, PyLong_FromLong(ps->eventParms[0]));
    PyTuple_SetItem(tuple, 31, PyLong_FromLong(ps->eventParms[1]));

    PyTuple_SetItem(tuple, 32, PyLong_FromLong(ps->externalEvent));
    PyTuple_SetItem(tuple, 33, PyLong_FromLong(ps->externalEventParm));
    PyTuple_SetItem(tuple, 34, PyLong_FromLong(ps->externalEventTime));

    PyTuple_SetItem(tuple, 35, PyLong_FromLong(ps->clientNum));
    PyTuple_SetItem(tuple, 36, PyLong_FromLong(ps->weapon));
    PyTuple_SetItem(tuple, 37, PyLong_FromLong(ps->weaponstate));

    PyTuple_SetItem(tuple, 38, PyFloat_FromDouble(ps->viewangles[0]));
    PyTuple_SetItem(tuple, 39, PyFloat_FromDouble(ps->viewangles[1]));
    PyTuple_SetItem(tuple, 40, PyFloat_FromDouble(ps->viewangles[2]));
    PyTuple_SetItem(tuple, 41, PyLong_FromLong(ps->viewheight));

    PyTuple_SetItem(tuple, 42, PyLong_FromLong(ps->damageEvent));
    PyTuple_SetItem(tuple, 43, PyLong_FromLong(ps->damageYaw));
    PyTuple_SetItem(tuple, 44, PyLong_FromLong(ps->damagePitch));
    PyTuple_SetItem(tuple, 45, PyLong_FromLong(ps->damageCount));

    int i;
    for(i = 0; i < 16; i++) {
        PyTuple_SetItem(tuple, 46 + i, PyLong_FromLong(ps->stats[i]));
        PyTuple_SetItem(tuple, 62 + i, PyLong_FromLong(ps->persistant[i]));
        PyTuple_SetItem(tuple, 78 + i, PyLong_FromLong(ps->powerups[i]));
        PyTuple_SetItem(tuple, 94 + i, PyLong_FromLong(ps->ammo[i]));
    }

    PyTuple_SetItem(tuple, 110, PyLong_FromLong(ps->generic1));
    PyTuple_SetItem(tuple, 111, PyLong_FromLong(ps->loopSound));
    PyTuple_SetItem(tuple, 112, PyLong_FromLong(ps->jumppad_ent));

    PyTuple_SetItem(tuple, 113, PyLong_FromLong(ps->ping));
    PyTuple_SetItem(tuple, 114, PyLong_FromLong(ps->pmove_framecount));
    PyTuple_SetItem(tuple, 115, PyLong_FromLong(ps->jumppad_frame));
    PyTuple_SetItem(tuple, 116, PyLong_FromLong(ps->entityEventSequence));
    return tuple;
}

void tupleToPlayerState(PyObject *tuple,  playerState_t *ps) {
    PyArg_ParseTuple(tuple, "iiiiifffff"\
                            "fiiiiiiiii"\
                            "iiifffiiii"\
                            "iiiiiiiiif"\
                            "ffiiiiiiii"\
                            "iiiiiiiiii"\
                            "iiiiiiiiii"\
                            "iiiiiiiiii"\
                            "iiiiiiiiii"\
                            "iiiiiiiiii"\
                            "iiiiiiiiii"\
                            "iiiiiii",
                     &(ps->commandTime),
                     &(ps->pm_type),
                     &(ps->bobCycle),
                     &(ps->pm_flags),
                     &(ps->pm_time),
                     
                     &(ps->origin[0]),
                     &(ps->origin[1]),
                     &(ps->origin[2]),
                     &(ps->velocity[0]),
                     &(ps->velocity[1]),
                     &(ps->velocity[2]),
                     &(ps->weaponTime),
                     &(ps->gravity),
                     &(ps->speed),
                     &(ps->delta_angles[0]),
                     &(ps->delta_angles[1]),
                     &(ps->delta_angles[2]),
                     
                     &(ps->groundEntityNum),
                     
                     &(ps->legsTimer),
                     &(ps->legsAnim),
                     
                     &(ps->torsoTimer),
                     &(ps->torsoAnim),
                     
                     &(ps->movementDir),
                     
                     &(ps->grapplePoint[0]),
                     &(ps->grapplePoint[1]),
                     &(ps->grapplePoint[2]),
                     
                     &(ps->eFlags),
                     
                     &(ps->eventSequence),
                     &(ps->events[0]),
                     &(ps->events[1]),
                     &(ps->eventParms[0]),
                     &(ps->eventParms[1]),
                     
                     &(ps->externalEvent),
                     &(ps->externalEventParm),
                     &(ps->externalEventTime),
                     
                     &(ps->clientNum),
                     &(ps->weapon),
                     &(ps->weaponstate),
                     
                     &(ps->viewangles[0]),
                     &(ps->viewangles[1]),
                     &(ps->viewangles[2]),
                     &(ps->viewheight),
                     
                     &(ps->damageEvent),
                     &(ps->damageYaw),
                     &(ps->damagePitch),
                     &(ps->damageCount),
                     
                     &(ps->stats[0]),
                     &(ps->stats[1]),
                     &(ps->stats[2]),
                     &(ps->stats[3]),
                     &(ps->stats[4]),
                     &(ps->stats[5]),
                     &(ps->stats[6]),
                     &(ps->stats[7]),
                     &(ps->stats[8]),
                     &(ps->stats[9]),
                     &(ps->stats[10]),
                     &(ps->stats[11]),
                     &(ps->stats[12]),
                     &(ps->stats[13]),
                     &(ps->stats[14]),
                     &(ps->stats[15]),
                     
                     &(ps->persistant[0]),
                     &(ps->persistant[1]),
                     &(ps->persistant[2]),
                     &(ps->persistant[3]),
                     &(ps->persistant[4]),
                     &(ps->persistant[5]),
                     &(ps->persistant[6]),
                     &(ps->persistant[7]),
                     &(ps->persistant[8]),
                     &(ps->persistant[9]),
                     &(ps->persistant[10]),
                     &(ps->persistant[11]),
                     &(ps->persistant[12]),
                     &(ps->persistant[13]),
                     &(ps->persistant[14]),
                     &(ps->persistant[15]),
                     
                     &(ps->powerups[0]),
                     &(ps->powerups[1]),
                     &(ps->powerups[2]),
                     &(ps->powerups[3]),
                     &(ps->powerups[4]),
                     &(ps->powerups[5]),
                     &(ps->powerups[6]),
                     &(ps->powerups[7]),
                     &(ps->powerups[8]),
                     &(ps->powerups[9]),
                     &(ps->powerups[10]),
                     &(ps->powerups[11]),
                     &(ps->powerups[12]),
                     &(ps->powerups[13]),
                     &(ps->powerups[14]),
                     &(ps->powerups[15]),
                     
                     &(ps->ammo[0]),
                     &(ps->ammo[1]),
                     &(ps->ammo[2]),
                     &(ps->ammo[3]),
                     &(ps->ammo[4]),
                     &(ps->ammo[5]),
                     &(ps->ammo[6]),
                     &(ps->ammo[7]),
                     &(ps->ammo[8]),
                     &(ps->ammo[9]),
                     &(ps->ammo[10]),
                     &(ps->ammo[11]),
                     &(ps->ammo[12]),
                     &(ps->ammo[13]),
                     &(ps->ammo[14]),
                     &(ps->ammo[15]),
                     
                     &(ps->generic1),
                     &(ps->loopSound),
                     &(ps->jumppad_ent),
                     
                     &(ps->ping),
                     &(ps->pmove_framecount),
                     &(ps->jumppad_frame),
                     &(ps->entityEventSequence));
}
