
import csv
import logging
import functools
import threading
from constants import *
from structs import *
from handles import *
from helpers import *


def log_exceptions(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Exception in {func.__name__}")
    return inner


class BaseScript:
    def __init__(self):
        self.active = False

    def on_start(self, arg):
        """Called when script is started by startscript console command"""
        pass

    def on_stop(self):
        """Called when script is stopped by stopscript console command"""
        pass

    @log_exceptions
    def run(self, callback, *args):
        if self.active or callback == "CL_StartScript":
            return getattr(self, callback)(*args)
        else:
            if len(args) == 1:
                return args[0]
            else:
                return args

    def CL_CreateCmd(self, cmd):
        return cmd

    def CL_StartScript(self, script_class_name, arg):
        """Arg is passed from the "startscript <scriptname> [<arg>] console command"""
        if script_class_name.lower() == self.__class__.__name__.lower():
            self.active = True
            self.on_start(arg)

    def CL_StopScript(self, script_class_name=None):
        if script_class_name is None or script_class_name.lower() == self.__class__.__name__.lower():
            self.active = False
            self.on_stop()

    def CL_ParseSnapshot(self, *args):
        return args


class DemoRecorder(BaseScript):
    pass


class UsercmdRecord(BaseScript):
    def __init__(self):
        super().__init__()
        self.csv_writer = None

    def CL_CreateCmd(self, cmd):
        self.csv_writer.writerow(tuple(cmd))
        return cmd

    def on_start(self, filename):
        self.csv_writer = csv.writer(open(filename, "w", newline=""))

    def on_stop(self):
        self.csv_writer = None


class UsercmdReplay(BaseScript):
    def __init__(self):
        super().__init__()
        self.csv_reader = None

    def CL_CreateCmd(self, cmd):
        # keep reading from csv file until we reached the end, then pass user input again
        # returns a tuple instead of usercmd_t class but this doesn't really matter atm
        if self.csv_reader is not None:
            try:
                row = list(map(int, next(self.csv_reader)))
                new_cmd = usercmd_t(*row)
                new_cmd.server_time = cmd.server_time
                return new_cmd
            except StopIteration:
                self.CL_StopScript()
        return cmd

    def on_start(self, filename):
        self.csv_reader = csv.reader(open(filename, "r"))

    def on_stop(self):
        self.csv_reader = None


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

    def on_start(self, _):
        kill()
        t =


class NiceWalkBot(BaseScript):
    def __init__(self):
        super().__init__()
        self.next_rightmove = MOVE_MAX
        self.start_time = None
        self.angle_offset = 6.075  # 405 @ 6

    def CL_CreateCmd(self, cmd):
        if self.start_time is None:
            self.start_time = cmd.server_time
        elif cmd.server_time - self.start_time < 350:
            # walk backwards for a bit into the back wall
            cmd.forwardmove = MOVE_MIN
        elif cmd.server_time - self.start_time < 475:
            # w only for a bit
            cmd.forwardmove = MOVE_MAX
        elif cmd.server_time - self.start_time < 14000:
            # walk forwards to end
            cmd.forwardmove = MOVE_MAX
            cmd.rightmove = self.next_rightmove
            cmd.angles_2 = degrees_to_angle(-90 + self.angle_offset)
            self.next_rightmove *= -1
            self.angle_offset *= -1
        else:
            self.CL_StopScript()
        return cmd

    def on_stop(self):
        self.start_time = None
        self.next_rightmove = MOVE_MAX
