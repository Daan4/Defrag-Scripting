import json
import csv
import g
from math import sqrt, pi, atan2, cos
from constants import *
import functools
import logging
from handles import get_cvar, set_cvar
import threading
import keyboard
import time


# decorator to log exceptions that occur in the decorated function
def log_exceptions(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            # Assumes that args[0] is self
            logging.exception(f"Exception in {func.__name__}")
    return inner


def angle_to_degrees(angle):
    return angle * 360 / 65536


def degrees_to_angle(degrees):
    return int((degrees * 65536/360) + 0.5) & 65535


def get_speed():
    return sqrt(g.ps.velocity[0] ** 2 + g.ps.velocity[1] ** 2)


def pause():
    set_cvar("cl_paused", "1")


def paused():
    if get_cvar("cl_paused") == "1":
        return True
    else:
        return False


def calc_fric_coeff(speed):
    if speed < 1:
        return 0
    if speed < 100:
        control = 100
    else:
        control = speed
    drop = control * 6 * 0.008
    if speed - drop < 0:
        return 0
    return (speed - drop) / speed


def calc_strafewalk_speed(w):
    """
    Calculates strafewalk speed (if holding +forward) given a certain wish angle.
    Maximize output to find optimal angle.
    input between theta_d - 0.5pi and theta_d + 0.5pi (pi and 2 pi), nicewalk-nowall 3/2pi is forward
    Assumes forwardmove = MOVE_MAX = 127

    Args:
        w: view angle yaw

    Returns:
        projected speed at view angle w

    """
    # W from short to angle in radians
    w = angle_to_degrees(w) * pi / 180
    theta_d = 3 * pi / 2
    speed = get_speed()
    f = calc_fric_coeff(speed)
    theta_v = atan2(g.ps.velocity[Y], g.ps.velocity[X])

    a = g.ps.speed - f * speed * cos(theta_v - w)
    if a < 0:
        a = 0
    elif a > 10 * 0.008 * g.ps.speed:
        a = 10 * 0.008 * g.ps.speed
    return f * speed * cos(theta_v - theta_d) + a * cos(w - theta_d)


def json_to_csv(jsonfile, csvfile):
    """Convert XPC recorded usercmd json format to my csv format"""
    x = json.load(open(jsonfile, "r"))
    writer = csv.writer(open(csvfile, "w", newline=""))
    for row in x:
        writer.writerow([row["serverTime"], row["angles"][0], row["angles"][1], row["angles"][2], row["buttons"], row["weapon"], row["forwardmove"], row["rightmove"], row["upmove"]])
