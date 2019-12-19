# usercmd_t value limits
MOVE_MAX = 127
MOVE_MIN = -127
ANGLE_MAX = 65535
ANGLE_MIN = 0

# From qcommon/q_shared.h
MOVE_RUN = 120  # if forwardmove or rightmove >= move_run: set button_walking

BUTTON_NONE = 0
BUTTON_ATTACK = 1
BUTTON_TALK = 2
BUTTON_USE_HOLDABLE = 4
BUTTON_GESTURE = 8
BUTTON_WALKING = 16
BUTTON_AFFIRMATIVE = 32
BUTTON_NEGATIVE = 64
BUTTON_GETFLAG = 128
BUTTON_GUARDBASE = 256
BUTTON_PATROL = 512
BUTTON_FOLLOWME = 1024
BUTTON_ANY = 2048
