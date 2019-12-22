from scripts_base_classes import StartScript
import g
from constants import *
from handles import get_predicted_playerstate


class UpdatePlayerState(StartScript):
    """Keep ps global up-to-date with latest playerState_t"""
    def __init__(self):
        super().__init__()

    def CL_ParseSnapshot(self, _ps):
        g.ps = _ps


class UpdateCommand(StartScript):
    """Modifies cmd.server_time to predictedplayerstate.command_time + 8
    Modify angles to account for delta angles
    (Should be defined after UpdatePlayerState class"""
    def __init__(self):
        super().__init__()

    def CL_CreateCmd(self, cmd):
        pps = get_predicted_playerstate()
        cmd.server_time = pps.command_time + 8
        cmd.angles[PITCH] += g.ps.delta_angles[PITCH]
        cmd.angles[YAW] += g.ps.delta_angles[YAW]
        cmd.angles[ROLL] += g.ps.delta_angles[ROLL]
        return cmd
