import json
import csv


# Convert usercmd_t angle to degrees from -90
# angle between 0 and 65535 inclusive
def angle_to_degrees(angle):
    angle = angle / 65535 * 360 - 90
    if angle > 180:
        angle = -180 + angle % 180
    return angle


# Convert degrees angle to usercmd_t
def degrees_to_angle(degrees):
    degrees = degrees % 360
    return int((degrees + 90) / 360 * 65535)


# Convert XPCs usercmd json files to csv
def json_to_csv(jsonfile, csvfile):
    x = json.load(open(jsonfile, "r"))
    writer = csv.writer(open(csvfile, "w", newline=""))
    for row in x:
        writer.writerow([row["serverTime"], row["angles"][0], row["angles"][1], row["angles"][2], row["buttons"], row["weapon"], row["forwardmove"], row["rightmove"], row["upmove"]])
