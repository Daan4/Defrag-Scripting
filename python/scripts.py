from constants import *
import csv
import logging
import functools
from structs import usercmd_t


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


class DemoRecorder(BaseScript):
    pass


class UsercmdRecorder(BaseScript):
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
