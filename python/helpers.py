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
    return (degrees + 90) / 360 * 65535
