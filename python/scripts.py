import functools
import logging
import threading
import time
from constants import *
from handles import echo, kill, get_predicted_playerstate, set_cl_viewangles
from helpers import do, stop, degrees_to_angle, angle_to_degrees

# Last known ps state, kept up to date by LatestPlayerState
ps = None


# decorator to log exceptions that occur in the decorated function
def log_exceptions(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            logging.exception(f"Exception in {func.__name__}")
    return inner


class BaseScript:
    def __init__(self):
        self.running = False

    def on_start(self, *args):
        """Called when script is started by startscript console command"""
        pass

    def on_stop(self):
        """Called when script is stopped by stopscript console command"""
        pass

    @log_exceptions
    def run(self, callback, *args):
        if self.running or callback == self.CL_StartScript.__name__:
            return getattr(self, callback)(*args)
        elif callback == self.CL_StopScript.__name__:
            return False  # If already running CL_StopScript calls should be returning False
        else:
            if len(args) == 1:
                return args[0]
            else:
                return args

    def CL_CreateCmd(self, cmd):
        return cmd

    def CL_StartScript(self, script_class_name=None, *args):
        if self.__class__.__name__ == "LatestPlayerState":
            logging.debug(f"{self.__class__.__name__} startscript, {script_class_name}")

        if script_class_name is None or script_class_name.lower() == self.__class__.__name__.lower() and not self.running:
            self.on_start(*args)
            self.running = True
            return True
        return False

    def CL_StopScript(self, script_class_name=None):
        if script_class_name is None or script_class_name.lower() == self.__class__.__name__.lower() and self.running:
            self.on_stop()
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


class UpdateViewAngles(FinalScript):
    """Update the cl->viewangles before returning the modified usercmd"""
    def __init__(self):
        super().__init__()

    def CL_CreateCmd(self, cmd):
        pitch = angle_to_degrees(cmd.angles[PITCH])
        yaw = angle_to_degrees(cmd.angles[YAW])
        roll = angle_to_degrees(cmd.angles[ROLL])
        set_cl_viewangles(pitch, yaw, roll)
        return cmd


class CommandTimeModifier(StartScript):
    """Modifies cmd.server_time to predictedplayerstate.command_time + 8"""
    def __init__(self):
        super().__init__()

    def CL_CreateCmd(self, cmd):
        pps = get_predicted_playerstate()
        if pps is not None:
            cmd.server_time = pps.command_time + 8
        return cmd


class LatestPlayerState(StartScript):
    """Keep ps global up-to-date with latest playerState_t"""
    def __init__(self):
        super().__init__()

    def CL_ParseSnapshot(self, _ps):
        global ps
        ps = _ps


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
            self.base_angle = angle_to_degrees(cmd.angles[YAW] + ps.delta_angles[YAW])

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

        cmd.angles[YAW] = degrees_to_angle(self.base_angle + self.angle_offset) - ps.delta_angles[YAW]
        self.next_movespeed *= -1
        self.angle_offset *= -1
        return cmd

    def on_start(self, direction, angle_deg=None, angle_offset_deg=0):
        self.base_angle = angle_deg
        self.angle_offset = angle_offset_deg
        self.direction = direction
        self.next_movespeed = MOVE_MAX


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
            self.start_angle = angle_to_degrees(cmd.angles[YAW] + ps.delta_angles[YAW])
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

        cmd.angles[YAW] = degrees_to_angle(self.angle) - ps.delta_angles[YAW]
        return cmd

    def on_start(self, direction, yaw_speed=295, end_angle_offset=90, start_angle=None):
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
        self.start_time = None
        self.prev_diff = None
        self.turnScript = None

    def CL_CreateCmd(self, cmd):
        if self.start_time is None:
            self.start_time = cmd.server_time
        diff = cmd.server_time - self.start_time
        if diff < 100:
            # walk backwards for a bit into the back wall
            do(Walk, BACKWARD)
        elif diff < 400:
            # walk forward up to at least 320 ups
            if self.prev_diff < 100:
                stop(Walk)
            do(Walk, FORWARD, -180)
        elif diff < 13500:
            if self.prev_diff < 400:
                stop(Walk)
            # cj turn into start trigger
            if self.turnScript is None:
                self.turnScript = do(CjTurn, LEFT, 295, 120, 150)
            if not self.turnScript.running:
                # walk forwards to end
                do(Walk, FORWARD, None, 6)
        else:
            stop(Walk)
            self.CL_StopScript()
        self.prev_diff = diff
        return cmd

    def on_stop(self):
        self.start_time = None
        self.turnScript = None
        stop(Walk)


if __name__ == "__main__":
    LatestPlayerState()
    Kill()
    EchoStuff()
    NiceWalk()
