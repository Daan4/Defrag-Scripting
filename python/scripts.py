import functools
import logging
import threading
import time
from constants import *
from handles import *
from helpers import do, stop, degrees_to_angle

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
        if self.running or callback == "CL_StartScript":
            return getattr(self, callback)(*args)
        elif callback == "CL_StopScript":
            return False
        else:
            if len(args) == 1:
                return args[0]
            else:
                return args

    def CL_CreateCmd(self, cmd):
        return cmd

    def CL_StartScript(self, script_class_name=None, *args):
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
        return _ps


class DefaultScript(BaseScript):
    # Same as BaseScript, but any class inheriting this will be started by CL_Init
    def __init__(self):
        super().__init__()


class LatestPlayerState(DefaultScript):
    # Keep ps global up-to-date with latest playerState_t
    def __init__(self):
        super().__init__()

    def CL_ParseSnapshot(self, _ps):
        global ps
        ps = _ps
        return _ps


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

    def on_start(self, direction, angle_deg, angle_offset_deg=0):
        self.base_angle = angle_deg - 90
        self.angle_offset = angle_offset_deg
        self.direction = direction
        self.next_movespeed = MOVE_MAX


class WalkTurn(BaseScript):
    # Yaws at max ups in a given direction until reaching a given angle
    pass


class EchoStuff(BaseScript):
    def __init__(self):
        super().__init__()

    def CL_ParseSnapshot(self, _ps):
        echo("CL_ParseSnapshot".rjust(20) + str(_ps.command_time).rjust(20) + str(time.time() * 1000).rjust(20))
        return _ps

    def CL_CreateCmd(self, cmd):
        echo("CL_CreateCmd".rjust(20) + str(cmd.server_time).rjust(20) + str(time.time() * 1000).rjust(20))
        return cmd


class NiceWalkBot(BaseScript):
    # nicewalk-nowall bot
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.prev_diff = None

    def CL_CreateCmd(self, cmd):
        if self.start_time is None:
            self.start_time = cmd.server_time
        diff = cmd.server_time - self.start_time
        if diff < 350:
            # walk backwards for a bit into the back wall
            do(Walk, BACKWARD, -90)
        elif diff < 450:
            # w only for a bit
            if self.prev_diff < 350:
                stop(Walk)
            do(Walk, FORWARD, -90)
        elif diff < 13000:
            # walk forwards to end
            if self.prev_diff < 450:
                stop(Walk)
            do(Walk, FORWARD, -90, 6)
        else:
            stop(Walk)
            do(Kill)
            self.CL_StopScript()
        self.prev_diff = diff
        return cmd

    def on_stop(self):
        self.start_time = None
        stop(Walk)


if __name__ == "__main__":
    LatestPlayerState()
    Kill()
    EchoStuff()
    NiceWalkBot()
