from constants import *


# Return a list of scripts to run
def init_scripts():
    x = TestScript()
    return [x]


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
