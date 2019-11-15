from constants import *
import csv
import logging
import functools
from structs import usercmd_t


# Return a list of scripts to run
def init_scripts():
    #x = TestScript()
    #x = UsercmdRecorderScript("test.csv")  # recorded as 15.496
    x = UsercmdReplayScript("test.csv")
    return [x]


def log_exceptions(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"Exception in {func.__name__}")
    return inner


class BaseScript:
    @log_exceptions
    def run(self, callback, *args):
        x = getattr(self, callback)(*args)
        return x

    def CL_CreateCmd(self, cmd):
        return cmd


class DemoRecorderScript(BaseScript):
    pass


class UsercmdRecorderScript(BaseScript):
    def __init__(self, filename):
        self.csv_writer = csv.writer(open(filename, "w", newline=''))

    def CL_CreateCmd(self, cmd):
        self.csv_writer.writerow(tuple(cmd))
        return cmd


class UsercmdReplayScript(BaseScript):
    def __init__(self, filename):
        self.csv_reader = csv.reader(open(filename, "r"))

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
                self.csv_reader = None
        return cmd
