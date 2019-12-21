import json
import csv


def do(script_class, *args):
    """Start a script and return the script instance
    Only start if the script is not already running"""
    from callbacks import CL_StartScript
    if not script_running(script_class):
        return CL_StartScript(script_class.__name__, *args)
    else:
        return None


def script_running(script_class):
    """Check if a script class is running or not."""
    from callbacks import script_instances
    for instance in script_instances:
        if instance.__class__ is script_class:
            return instance.running


# Stop a script from within another script
def stop(script_class):
    """Stop a script"""
    from callbacks import CL_StopScript
    return CL_StopScript(script_class.__name__)


def angle_to_degrees(angle):
    """Convert usercmd_t angle to degrees from -90
    angle between 0 and 65535 inclusive"""
    return angle * 360 / 65536


def degrees_to_angle(degrees):
    """Convert degrees angle to usercmd_t"""
    return int((degrees * 65536/360)) & 65535


def json_to_csv(jsonfile, csvfile):
    """Convert XPC recorded usercmd json format to my csv format"""
    x = json.load(open(jsonfile, "r"))
    writer = csv.writer(open(csvfile, "w", newline=""))
    for row in x:
        writer.writerow([row["serverTime"], row["angles"][0], row["angles"][1], row["angles"][2], row["buttons"], row["weapon"], row["forwardmove"], row["rightmove"], row["upmove"]])
