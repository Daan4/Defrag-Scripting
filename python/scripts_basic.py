from scripts_base_classes import BasicScript
from constants import *
from handles import kill
from helpers import degrees_to_angle, calc_strafewalk_speed
import g
import threading
import logging


class Kill(BasicScript):
    # Combines /kill and +attack to respawn
    def __init__(self):
        super().__init__()
        self.shoot = False

    def CL_CreateCmd(self, cmd):
        if self.shoot:
            cmd.buttons |= BUTTON_ATTACK
            self.shoot = False
            self.CL_StopScript()
        return cmd

    def respawn(self):
        self.shoot = True

    def on_start(self):
        kill()
        threading.Timer(0.1, self.respawn).start()


class Walk(BasicScript):
    # Walk in a given direction, with an optional angle offset to strafe-walk
    def __init__(self):
        super().__init__()
        self.next_movespeed = MOVE_MAX
        self.angle_offset = None  # ~max 405 ups @ 6
        self.base_angle = None
        self.direction = None
        self.switch_delay = None
        self.frames_since_switch = None

    def CL_CreateCmd(self, cmd):
        if self.base_angle is None:
            self.base_angle = g.ps.view_angles[YAW]

        if self.direction == FORWARD:
            cmd.forwardmove = MOVE_MAX
            if self.angle_offset != 0:
                cmd.rightmove = self.next_movespeed
        elif self.direction == BACKWARD:
            cmd.forwardmove = MOVE_MIN
            if self.angle_offset != 0:
                cmd.rightmove = self.next_movespeed
        elif self.direction == LEFT:
            cmd.rightmove = MOVE_MIN
            if self.angle_offset != 0:
                cmd.forwardmove = self.next_movespeed
        elif self.direction == RIGHT:
            cmd.rightmove = MOVE_MAX
            if self.angle_offset != 0:
                cmd.forwardmove = self.next_movespeed

        cmd.angles[YAW] = degrees_to_angle(self.base_angle + self.angle_offset)
        if self.frames_since_switch == self.switch_delay:
            self.next_movespeed *= -1
            self.angle_offset *= -1
            self.frames_since_switch = 0
        else:
            self.frames_since_switch += 1
        return cmd

    def on_start(self, direction, angle_deg=None, angle_offset_deg=0, switch_delay=0):
        """
        Args:
            direction: Movement button to hold [FORWARD BACKWARD LEFT RIGHT]
            angle_deg: Angle to walk in
            angle_offset_deg: Angle offset for strafe-walking; positive starts right, negative starts left
            switch_delay: Time in frames between direction switches
        """
        self.switch_delay = switch_delay
        self.frames_since_switch = 0
        self.base_angle = angle_deg
        self.angle_offset = angle_offset_deg
        if self.angle_offset < 0:
            # Start in reverse direction
            self.next_movespeed = MOVE_MIN
        else:
            self.next_movespeed = MOVE_MAX
        self.direction = direction


class WalkAuto(BasicScript):
    """Automatically strafewalk in a given direction"""
    def __init__(self):
        super().__init__()

    def CL_CreateCmd(self, cmd):
        best_angle = 0
        best_speed = 0
        for i in range(37769, 60536, 12):
            speed = calc_strafewalk_speed(i)
            if speed > best_speed:
                best_angle = i
                best_speed = speed
        best_speed = 0
        for i in range(best_angle - 12, best_angle + 12):
            speed = calc_strafewalk_speed(i)
            if speed > best_speed:
                best_angle = i
                best_speed = speed
        cmd.angles[YAW] = best_angle
        cmd.forwardmove = MOVE_MAX
        return cmd


class CjTurn(BasicScript):
    """Turn in a given direction until reaching a given angle while holding forward+strafe
    Yawspeed is given in angle/sec change, and defaults to optimal-ish yawspeed (vq3)
    Will turn start_angle to start_angle + end_angle_offset in direction LEFT or RIGHT
    If start_angle=None the initial angle is used as start angle
    """
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.yaw_speed = None
        self.direction = None
        self.start_angle = None
        self.angle = None
        self.end_angle_offset = None

    def CL_CreateCmd(self, cmd):
        if self.start_angle is None:
            self.start_angle = g.ps.view_angles[YAW]
        if self.start_time is None:
            self.start_time = cmd.server_time
        self.angle = self.start_angle

        diff = cmd.server_time - self.start_time
        cmd.forwardmove = MOVE_MAX
        if self.direction == LEFT:
            cmd.rightmove = MOVE_MIN
            self.angle = self.start_angle + diff / ((self.end_angle_offset - self.start_angle) / self.yaw_speed * 1000) * (self.end_angle_offset - self.start_angle)
        elif self.direction == RIGHT:
            cmd.rightmove = MOVE_MAX
            self.angle = self.start_angle + diff / ((self.start_angle - self.end_angle_offset) / self.yaw_speed * 1000) * (self.end_angle_offset - self.start_angle)

        if self.angle >= self.start_angle + self.end_angle_offset:
            self.angle = self.start_angle + self.end_angle_offset
            cmd.rightmove = 0
            cmd.forwardmove = 0
            self.CL_StopScript()

        cmd.angles[YAW] = degrees_to_angle(self.angle)
        return cmd

    def on_start(self, direction, end_angle_offset=90, start_angle=None, yaw_speed=295):
        """
        Args:
            direction: Turn direction [LEFT RIGHT]
            end_angle_offset: Turn angle in degrees (this + start_angle == final angle)
            start_angle: Starting angle, None uses the current viewangle
            yaw_speed: Turn speed in degrees/second
        """
        self.yaw_speed = yaw_speed
        self.direction = direction
        self.start_angle = start_angle
        self.angle = None
        self.end_angle_offset = end_angle_offset
        self.start_time = None
