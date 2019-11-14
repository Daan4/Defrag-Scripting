from constants import *
import csv
import logging


# Return a list of scripts to run
def init_scripts():
    #x = TestScript()
    #x = UsercmdRecorderScript("test.csv")  # recorded as 15.496
    x = UsercmdReplayScript("test.csv")
    return [x]


class DemoRecorderScript:
    pass


class UsercmdRecorderScript:
    def __init__(self, filename):
        self.csv_writer = csv.writer(open(filename, "w", newline=''))

    def run(self, callback_name, *args):
        if callback_name == "CL_CreateCmd":
            return self.write(*args)

    def write(self, cmd):
        self.csv_writer.writerow(tuple(cmd))
        return cmd


class UsercmdReplayScript:
    def __init__(self, filename):
        self.csv_reader = csv.reader(open(filename, "r"))

    def run(self, callback_name, *args):
        if callback_name == "CL_CreateCmd":
            return self.read(*args)

    def read(self, cmd):
        # keep reading from csv file until we reached the end, then pass user input again
        if self.csv_reader is not None:
            try:
                row = list(map(int, next(self.csv_reader)))
                return tuple([cmd.server_time] + row[1:])
            except StopIteration:
                self.csv_reader = None
        return tuple([cmd.server_time] + list(cmd))
