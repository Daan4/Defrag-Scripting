from scripts_base_classes import BotScript
from constants import *
from helpers import get_speed
import g
from scripts_basic import Kill, Walk, CjTurn, WalkAuto


class NiceWalk(BotScript):
    # nicewalk-nowall bot
    def __init__(self):
        super().__init__()

    def init_script_sequence(self):
        # self.wait_after_script = False
        # self.wait_after_frame = True
        #
        # self.add(Walk, lambda: g.ps.origin[Y] >= 464, BACKWARD)
        # self.add(WalkAuto, lambda: g.ps.stats[TIMER_CP_HIT] == 524)


        self.wait_after_frame = True
        self.wait_after_script = False

        self.add(Walk, lambda: g.ps.origin[Y] >= 464, BACKWARD)
        self.add(Walk, lambda: get_speed() == 320, FORWARD, -180)
        self.add(CjTurn, None, LEFT, 96, -180)
        self.add(Walk, lambda: g.ps.stats[TIMER_CP_HIT] == 524, FORWARD, -90, -6)

        # Experiment with walking
        # self.add(Walk, lambda: g.ps.origin[Y] >= 464, BACKWARD)
        # self.add(Walk, lambda: g.ps.stats[TIMER_CP_HIT] == 524, FORWARD, angle_offset_deg=6, switch_delay=4)
