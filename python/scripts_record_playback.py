import csv
from scripts_base_classes import BasicScript
from structs import usercmd_t


class DemoRecorder(BasicScript):
    pass


class UsercmdRecord(BasicScript):
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


class UsercmdReplay(BasicScript):
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
