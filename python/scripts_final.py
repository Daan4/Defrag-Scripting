from scripts_base_classes import FinalScript
from helpers import angle_to_degrees
from handles import set_cl_viewangles, echo
from constants import *
import time
import g


class UpdateAngles(FinalScript):
    """Modify command angles with ps delta angles, then update the cl->viewangles"""
    def __init__(self):
        super().__init__()

    def CL_CreateCmd(self, cmd):
        cmd.angles[PITCH] -= g.ps.delta_angles[PITCH]
        cmd.angles[YAW] -= g.ps.delta_angles[YAW]
        cmd.angles[ROLL] -= g.ps.delta_angles[ROLL]
        pitch = angle_to_degrees(cmd.angles[PITCH])
        yaw = angle_to_degrees(cmd.angles[YAW])
        roll = angle_to_degrees(cmd.angles[ROLL])
        set_cl_viewangles(pitch, yaw, roll)
        return cmd


class EchoStuff(FinalScript):
    def __init__(self):
        super().__init__()
        self.autostart = False

    def CL_ParseSnapshot(self, _ps):
        #echo(self.CL_ParseSnapshot.__name__.rjust(20) + str(_ps.command_time).rjust(20) + str(time.time() * 1000).rjust(20))
        echo(str(_ps.stats[12]))
        # 512 -> 518 -> 524

    def CL_CreateCmd(self, cmd):
        #echo(self.CL_CreateCmd.__name__.rjust(20) + str(cmd.server_time).rjust(20) + str(time.time() * 1000).rjust(20))
        return cmd

