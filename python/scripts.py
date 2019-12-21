import logging
import functools
import threading
import time
from constants import *
from handles import *
from helpers import *
import callbacks

ps = None


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
        self.stop_event = threading.Event()
        self.stop_event.set()

    def on_start(self, arg):
        """Called when script is started by startscript console command"""
        pass

    def on_stop(self):
        """Called when script is stopped by stopscript console command"""
        pass

    def is_running(self):
        return not self.stop_event.is_set()

    @log_exceptions
    def run(self, callback, *args):
        if not self.stop_event.is_set() or callback == "CL_StartScript":
            return getattr(self, callback)(*args)
        else:
            if len(args) == 1:
                return args[0]
            else:
                return args

    def CL_CreateCmd(self, cmd):
        return cmd

    def CL_StartScript(self, script_class_name=None, arg=None):
        """Arg is passed from the "startscript <scriptname> [<arg>] console command"""
        if script_class_name is None or script_class_name.lower() == self.__class__.__name__.lower() and not self.is_running():
            self.stop_event.clear()
            self.on_start(arg)
            return True
        return False

    def CL_StopScript(self, script_class_name=None):
        if script_class_name is None or script_class_name.lower() == self.__class__.__name__.lower() and self.is_running():
            self.stop_event.set()
            self.on_stop()
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


class KillScript(BaseScript):
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

    def on_start(self, _):
        kill()
        threading.Timer(0.1, self.respawn).start()


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
        self.next_rightmove = MOVE_MAX
        self.start_time = None
        self.killScript = None

        # Settings
        self.iteration = 0
        self.angle_offset_change = 0.1
        self.angle_offset = 5.5  # 405 @ 6

    def CL_CreateCmd(self, cmd):
        if self.start_time is None:
            self.start_time = cmd.server_time
        elif cmd.server_time - self.start_time < 350:
            # walk backwards for a bit into the back wall
            cmd.forwardmove = MOVE_MIN
        elif cmd.server_time - self.start_time < 450:
            # w only for a bit
            cmd.forwardmove = MOVE_MAX
        elif cmd.server_time - self.start_time < 13000:
            # walk forwards to end
            cmd.forwardmove = MOVE_MAX
            cmd.rightmove = self.next_rightmove
            cmd.angles[YAW] = degrees_to_angle(180 + self.angle_offset) - ps.delta_angles[YAW]
            self.next_rightmove *= -1
            self.angle_offset *= -1
        else:
            if self.killScript is None:
                self.killScript = callbacks.CL_StartScript(KillScript.__name__)
            elif not self.killScript.is_running():
                self.killScript = None
                self.start_time = None
                self.next_rightmove = abs(self.next_rightmove)
                self.angle_offset = abs(self.angle_offset)
                self.angle_offset += self.angle_offset_change
        return cmd

    def on_stop(self):
        self.start_time = None
        self.next_rightmove = MOVE_MAX


if __name__ == "__main__":
    LatestPlayerState()
    KillScript()
    EchoStuff()
    NiceWalkBot()
