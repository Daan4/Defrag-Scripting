from scripts_base_classes import BotScript
from constants import *
from helpers import get_speed
import g
from scripts_base import Kill, Walk, CjTurn


class NiceWalk(BotScript):
    # nicewalk-nowall bot
    def __init__(self):
        super().__init__()

    def init_script_sequence(self):
        self.add_script(Walk, lambda: g.ps.origin[Y] >= 455, BACKWARD)
        self.add_script(Walk, lambda: get_speed() == 320, FORWARD, -180)
        self.add_script(CjTurn, None, LEFT, 120, 150)
        self.add_script(Walk, lambda: get_speed() == 0, FORWARD, angle_offset_deg=-6)
