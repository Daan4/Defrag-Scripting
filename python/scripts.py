import functools
import logging
import threading
import time
from constants import *
from handles import echo, kill, get_predicted_playerstate, set_cl_viewangles
from helpers import degrees_to_angle, angle_to_degrees, get_speed
import g


# decorator to log exceptions that occur in the decorated function
def log_exceptions(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            # Assumes that args[0] is self
            logging.exception(f"Exception in {args[0].__class__.__name__}")
    return inner


class BaseScript:
    def __init__(self):
        self.running = False  # True if script is running
        self.waiting = False  # True if script is waiting
        self.prev_waiting = False  # Waiting state of previous frame, used to detect script finish in the callback
        self.wait_script = None  # Instance of the script that the current script is waiting on, or None
        self.stop_condition = None  # A function which auto-stops the script if it evaluates to True

    def on_start(self, *args, **kwargs):
        """Called when script is started by startscript console command"""
        pass

    def on_stop(self):
        """Called when script is stopped by stopscript console command"""
        pass

    def do(self, script_class, stop_condition=lambda: False, *args, **kwargs):
        """Start another script, and if a stop_condition is given wait for it to finish."""
        for instance in g.script_instances:
            if script_class is instance.__class__:
                if stop_condition is not None:
                    self.wait(instance)
                instance.CL_StartScript(script_class.__name__, stop_condition, *args, **kwargs)
                return instance

    def wait(self, instance):
        self.wait_script = instance
        self.prev_waiting = self.waiting
        self.waiting = True

    def wait_done(self):
        """Can be called to check if the wait finished this frame"""
        return self.prev_waiting and not self.waiting


    def on_wait(self):
        if not self.wait_script.running:
            self.wait_script = None
            self.prev_waiting = self.waiting
            self.waiting = False

    @log_exceptions
    def run(self, callback, *args, **kwargs):
        if self.waiting:
            self.on_wait()

        if callback == self.CL_StartScript.__name__:
            return self.CL_StartScript(*args, **kwargs)
        elif self.running and not self.waiting:
            if not self.stop_condition():
                # Fire the callback
                return getattr(self, callback)(*args, **kwargs)
            else:
                self.CL_StopScript()
        elif self.waiting and callback == self.CL_StopScript.__name__:
            # Still allow script to be stopped while waiting
            return self.CL_StopScript(*args, **kwargs)

        # Return the original args if the callback wasn't fired
        if len(args) == 1:
            return args[0]
        else:
            return args

    def CL_CreateCmd(self, cmd):
        return cmd

    def CL_StartScript(self, script_class_name=None, stop_condition=lambda: False, *args, **kwargs):
        if script_class_name is None:
            script_class_name = self.__class__.__name__
        if script_class_name.lower() == self.__class__.__name__.lower() and not self.running:
            logging.debug(f"Starting script \"{script_class_name}\" with args \"{args}\" and kwargs \"{kwargs}\"")
            self.on_start(*args, **kwargs)
            self.stop_condition = stop_condition
            self.running = True
            return True
        return False

    def CL_StopScript(self, script_class_name=None):
        if script_class_name is None:
            script_class_name = self.__class__.__name__
        if script_class_name.lower() == self.__class__.__name__.lower() and self.running:
            logging.debug(f"Stopping script \"{script_class_name}\"")
            self.on_stop()
            self.wait_script = None
            self.waiting = False
            self.prev_waiting = False
            self.running = False
            return True
        return False

    def CL_ParseSnapshot(self, _ps):
        pass


class StartScript(BaseScript):
    """Same as BaseScript, but any class inheriting this will be started by CL_Init
    Default scripts also get called first, before any of the other registered scripts.
    """
    def __init__(self):
        super().__init__()


class FinalScript(BaseScript):
    """Same as StartScript, except these get called last after any of the other registered scripts.
    """
    def __init__(self):
        super().__init__()


class BotScript(BaseScript):
    """Same as BaseScript, but these are called before BaseScripts
    This allows any BaseScript started in a BotScript to start in the same frame.
    """
    def __init__(self):
        super().__init__()


class UpdateAngles(FinalScript):
    """Modify command angles with ps delta angles, then update the cl->viewangles"""
    def __init__(self):
        super().__init__()

    def CL_CreateCmd(self, cmd):
        cmd.angles[PITCH] -= g.ps.delta_angles[PITCH]
        cmd.angles[YAW] -= g.ps.delta_angles[YAW]
        cmd.angles[ROLL] -= g.ps.delta_angles[ROLL]
        pitch = angle_to_degrees(cmd.angles[PITCH])
        yaw = angle_to_degrees(cmd.angles[YAW])
        roll = angle_to_degrees(cmd.angles[ROLL])
        set_cl_viewangles(pitch, yaw, roll)
        return cmd


class UpdatePlayerState(StartScript):
    """Keep ps global up-to-date with latest playerState_t"""
    def __init__(self):
        super().__init__()

    def CL_ParseSnapshot(self, _ps):
        g.ps = _ps


class UpdateCommand(StartScript):
    """Modifies cmd.server_time to predictedplayerstate.command_time + 8
    Modify angles to account for delta angles
    (Should be defined after UpdatePlayerState class"""
    def __init__(self):
        super().__init__()

    def CL_CreateCmd(self, cmd):
        pps = get_predicted_playerstate()
        cmd.server_time = pps.command_time + 8
        cmd.angles[PITCH] += g.ps.delta_angles[PITCH]
        cmd.angles[YAW] += g.ps.delta_angles[YAW]
        cmd.angles[ROLL] += g.ps.delta_angles[ROLL]
        return cmd


class Kill(BaseScript):
    # Combines /kill and +attack to respawn
    def __init__(self):
        super().__init__()
        self.shoot = False

    def CL_CreateCmd(self, cmd):
        if self.shoot:
            cmd.buttons |= BUTTON_ATTACK
            self.shoot = False
            self.CL_StopScript()
        return cmd

    def respawn(self):
        self.shoot = True

    def on_start(self):
        kill()
        threading.Timer(0.1, self.respawn).start()


class Walk(BaseScript):
    # Walk in a given direction, with an optional angle offset to strafe-walk
    def __init__(self):
        super().__init__()
        self.next_movespeed = MOVE_MAX
        self.angle_offset = None  # ~max 405 ups @ 6
        self.base_angle = None
        self.direction = None

    def CL_CreateCmd(self, cmd):
        if self.base_angle is None:
            self.base_angle = g.ps.view_angles[YAW]

        if self.direction == FORWARD:
            cmd.forwardmove = MOVE_MAX
            if self.angle_offset != 0:
                cmd.rightmove = self.next_movespeed
        elif self.direction == BACKWARD:
            cmd.forwardmove = MOVE_MIN
            if self.angle_offset != 0:
                cmd.rightmove = self.next_movespeed
        elif self.direction == LEFT:
            cmd.rightmove = MOVE_MIN
            if self.angle_offset != 0:
                cmd.forwardmove = self.next_movespeed
        elif self.direction == RIGHT:
            cmd.rightmove = MOVE_MAX
            if self.angle_offset != 0:
                cmd.forwardmove = self.next_movespeed

        cmd.angles[YAW] = degrees_to_angle(self.base_angle + self.angle_offset)
        self.next_movespeed *= -1
        self.angle_offset *= -1
        return cmd

    def on_start(self, direction, angle_deg=None, angle_offset_deg=0):
        self.base_angle = angle_deg
        self.angle_offset = angle_offset_deg
        if self.angle_offset < 0:
            # Start in reverse direction
            self.next_movespeed = MOVE_MIN
        else:
            self.next_movespeed = MOVE_MAX
        self.direction = direction


class CjTurn(BaseScript):
    """Turn in a given direction until reaching a given angle while holding forward+strafe
    Yawspeed is given in angle/sec change, and defaults to optimal-ish yawspeed (vq3)
    Will turn start_angle to start_angle + end_angle_offset in direction LEFT or RIGHT
    If start_angle=None the initial angle is used as start angle
    """
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.yaw_speed = None
        self.direction = None
        self.start_angle = None
        self.angle = None
        self.end_angle_offset = None

    def CL_CreateCmd(self, cmd):
        if self.start_angle is None:
            self.start_angle = g.ps.view_angles[YAW]
        if self.start_time is None:
            self.start_time = cmd.server_time
        self.angle = self.start_angle

        diff = cmd.server_time - self.start_time
        cmd.forwardmove = MOVE_MAX
        if self.direction == LEFT:
            cmd.rightmove = MOVE_MIN
            self.angle = self.start_angle + diff / ((self.end_angle_offset - self.start_angle) / self.yaw_speed * 1000) * (self.end_angle_offset - self.start_angle)
        elif self.direction == RIGHT:
            cmd.rightmove = MOVE_MAX
            self.angle = self.start_angle + diff / ((self.start_angle - self.end_angle_offset) / self.yaw_speed * 1000) * (self.end_angle_offset - self.start_angle)

        if self.angle >= self.start_angle + self.end_angle_offset:
            self.angle = self.start_angle + self.end_angle_offset
            cmd.rightmove = 0
            cmd.forwardmove = 0
            self.CL_StopScript()

        cmd.angles[YAW] = degrees_to_angle(self.angle)
        return cmd

    def on_start(self, direction, end_angle_offset=90, start_angle=None, yaw_speed=295):
        self.yaw_speed = yaw_speed
        self.direction = direction
        self.start_angle = start_angle
        self.angle = None
        self.end_angle_offset = end_angle_offset
        self.start_time = None


class EchoStuff(BaseScript):
    def __init__(self):
        super().__init__()

    def CL_ParseSnapshot(self, _ps):
        echo("CL_ParseSnapshot".rjust(20) + str(_ps.command_time).rjust(20) + str(time.time() * 1000).rjust(20))

    def CL_CreateCmd(self, cmd):
        echo("CL_CreateCmd".rjust(20) + str(cmd.server_time).rjust(20) + str(time.time() * 1000).rjust(20))
        return cmd


class NiceWalk(BotScript):
    # nicewalk-nowall bot
    def __init__(self):
        super().__init__()

    def CL_CreateCmd(self, cmd):
        if self.wait_done():
            self.CL_StopScript()
        else:
            self.do(Walk, lambda: get_speed() >= 300, FORWARD)
        return cmd

        # if self.start_time is None:
        #     self.start_time = cmd.server_time
        # diff = cmd.server_time - self.start_time
        # if diff < 75:
        #     # walk backwards for a bit into the back wall
        #     do(Walk, BACKWARD)
        # elif diff < 400:
        #     # walk forward up to at least 320 ups
        #     if self.prev_diff < 75:
        #         stop(Walk)
        #     do(Walk, FORWARD, -180)
        # elif diff < 13500:
        #     if self.prev_diff < 400:
        #         stop(Walk)
        #     # cj turn into start trigger
        #     if not self.turned:
        #         do(CjTurn, LEFT, 120, start_angle=150)
        #         return cmd
        #     do(Walk, FORWARD, None, -6)
        # else:
        #     stop(Walk)
        #     self.CL_StopScript()
        # self.prev_diff = diff
        # return cmd


if __name__ == "__main__":
    UpdatePlayerState()
    Kill()
    EchoStuff()
    NiceWalk()
