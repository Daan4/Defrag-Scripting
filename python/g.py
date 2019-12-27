"""Global state"""

# List of script instances (All classes derived from BaseScript)
# Populated in CL_Init callback
script_instances = None

# Last known playerState_t, kept up to date by LatestPlayerState StartScript
ps = None

pause_next_frame = False
