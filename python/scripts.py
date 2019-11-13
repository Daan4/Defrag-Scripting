from constants import *
import csv
import logging

# Return a list of scripts to run
def init_scripts():
    #x = TestScript()
    x = LiveRecorderScript("test.csv")  # 15:104
    #x = ReplayScript("test.csv")
    return [x]


class DemoRecorderScript:
    pass


class LiverecorderScript:
    def __init__(self, filename):
        self.csv_writer = csv.writer(open(filename, "w", newline=''))

    def run(self, callback_name, *args):
        if callback_name == "CL_CreateCmd":
            return self.write(*args)

    def write(self, *args):
        self.csv_writer.writerow(args)
        return args


class ReplayScript:
    def __init__(self, filename):
        self.csv_reader = csv.reader(open(filename, "r"))

    def run(self, callback_name, *args):
        if callback_name == "CL_CreateCmd":
            return self.read(*args)

    def read(self, server_time, *args):
            # keep reading from csv file until we reached the end, then pass user input again
        if self.csv_reader is not None:
            try:
                row = list(map(int, next(self.csv_reader)))
                return tuple([server_time] + row[1:])
            except StopIteration:
                self.csv_reader = None
        return tuple([server_time] + list(args))


class TestScript:
    def __init__(self):
        self.angles = [0, 16384, 32768, 49152]

    def run(self, callback_name, *args):
        if callback_name == "CL_CreateCmd":
            return self.test_angles(*args)

    def test_angles(self, server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove):
        x = server_time % 20000
        if x < 5000:
            angles = self.angles[0]
        elif x < 10000:
            angles = self.angles[1]
        elif x < 15000:
            angles = self.angles[2]
        elif x < 20000:
            angles = self.angles[3]
        angles_2 = angles

        return server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove
