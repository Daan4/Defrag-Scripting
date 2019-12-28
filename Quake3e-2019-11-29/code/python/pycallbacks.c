#include "pycallbacks.h"

// Python file and function names
const char *CALLBACKS_FILENAME = "callbacks";
const char *CL_INITCGAME_FUNCTION = "CL_InitCGame";
const char *CL_INIT_FUNCTION = "CL_Init";
const char *CL_CREATECMD_FUNCTION = "CL_CreateCmd";
const char *CL_STARTSCRIPT_FUNCTION = "CL_StartScript";
const char *CL_STOPSCRIPT_FUNCTION = "CL_StopScript";
const char *CL_PARSESNAPSHOT_FUNCTION = "CL_ParseSnapshot";
const char *CL_LOGMESSAGE_FUNCTION = "CL_LogMessage";

PyObject *CALLBACK_MODULE;

// Expose C functions to python
static PyMethodDef Methods[] = {
    {"Py_Cbuf_ExecuteText", Py_Cbuf_ExecuteText, METH_VARARGS, "Execute a console command."},
    {"Py_GetPredictedPlayerstate", Py_GetPredictedPlayerstate, METH_VARARGS, "Get predicted playerstate."},
    {"Py_UpdateViewangles", Py_UpdateViewangles, METH_VARARGS, "Update cl->viewangles."},
    {"Py_Cvar_Set", Py_Cvar_Set, METH_VARARGS, "Set Cvar value (outside of console as with Cbuf_ExecuteText)."},
    {"Py_Cvar_Get", Py_Cvar_Get, METH_VARARGS, "Get Cvar value."},
    {"Py_TestFunction", Py_TestFunction, METH_VARARGS, "Testing Function"},
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

void Py_ReloadPython(void) {
    Py_FinalizeEx();
    Py_CL_Init();
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
    PyObject_CallObject(Func, Args);

    Py_DECREF(Args);
    Py_DECREF(Func);
}

void Py_CL_LogMessage(const char *message) {
    PyObject *Args = PyTuple_New(1);
    PyTuple_SetItem(Args, 0, PyUnicode_FromString(message));

    PyObject *Func = PyObject_GetAttrString(CALLBACK_MODULE, CL_LOGMESSAGE_FUNCTION);
    PyObject_CallObject(Func, Args);

    Py_DECREF(Args);
    Py_DECREF(Func);
}

// FUNCTION HANDLES CALLABLE FROM PYTHON
// Execute console commands
// args:
//          cmd [string]: console command to send. Must end with a newline (\n)
PyObject *Py_Cbuf_ExecuteText(PyObject *self, PyObject *args)
{
    char *command;
    if(!PyArg_ParseTuple(args, "s", &command))
        return NULL;

    Cbuf_ExecuteText(EXEC_NOW, command);

    Py_RETURN_NONE;
}

PyObject *Py_GetPredictedPlayerstate(PyObject *self, PyObject *args)
{
    // read predicted playerstate from defrag binary memory
    // offset depends on defrag version this is for .25
    return playerStateToTuple((playerState_t *)(cgvm->dataBase + 957848));
}

PyObject *Py_UpdateViewangles(PyObject *self, PyObject *args)
{
    float pitch, yaw, roll;
    if(!PyArg_ParseTuple(args, "fff", &pitch, &yaw, &roll))
        return NULL;

    cl.viewangles[0] = pitch;
    cl.viewangles[1] = yaw;
    cl.viewangles[2] = roll;

    Py_RETURN_NONE;
}


PyObject *Py_Cvar_Get(PyObject *self, PyObject *args)
{
    char *name;
    const char *value = "0";
    if(!PyArg_ParseTuple(args, "s", &name))
        return NULL;

    cvar_t *cv = Cvar_Get(name, value, 0);

    return PyUnicode_FromString(cv->string);
}

PyObject *Py_Cvar_Set(PyObject *self, PyObject *args)
{
    char *name;
    char *value;
    if(!PyArg_ParseTuple(args, "ss", &name, &value))
        return NULL;

    Cvar_Set(name, value);

    Py_RETURN_NONE;
}

PyObject *Py_TestFunction(PyObject *self, PyObject *args)
{
    // Function that can be used for testing purposes
    int angle_int = ANGLE2SHORT(0.1);
    double angle_deg = SHORT2ANGLE(angle_int);
    return PyFloat_FromDouble(angle_deg);
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
