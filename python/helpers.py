import json
import csv
import g
from math import sqrt


def angle_to_degrees(angle):
    return angle * 360 / 65536


def degrees_to_angle(degrees):
    return int((degrees * 65536/360) + 0.5) & 65535


def get_speed():
    return sqrt(g.ps.velocity[0] ** 2 + g.ps.velocity[1] ** 2)


def json_to_csv(jsonfile, csvfile):
    """Convert XPC recorded usercmd json format to my csv format"""
    x = json.load(open(jsonfile, "r"))
    writer = csv.writer(open(csvfile, "w", newline=""))
    for row in x:
        writer.writerow([row["serverTime"], row["angles"][0], row["angles"][1], row["angles"][2], row["buttons"], row["weapon"], row["forwardmove"], row["rightmove"], row["upmove"]])
