# Data container classes to mirror the C structs
class BaseStruct:
    def __iter__(self):
        for _, v in self.__dict__.items():
            if isinstance(v, list):
                for x in v:
                    yield x
            else:
                yield v

    def __repr__(self):
        return " ".join([str(v) for _, v in self.__dict__.items()])


class usercmd_t(BaseStruct):
    def __init__(self, server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove):
        self.server_time = server_time
        self.angles = [angles_1, angles_2, angles_3]
        self.buttons = buttons
        self.weapon = weapon
        self.forwardmove = forwardmove
        self.rightmove = rightmove
        self.upmove = upmove


class playerState_t(BaseStruct):
    def __init__(self, *args):
        self.command_time = args[0]
        self.pm_type = args[1]
        self.bob_cycle = args[2]
        self.pm_flags = args[3]
        self.pm_time = args[4]

        self.origin = [args[5], args[6], args[7]]
        self.velocity = [args[8], args[9], args[10]]
        self.weapon_time = args[11]
        self.gravity = args[12]
        self.speed = args[13]
        self.delta_angles = [args[14], args[15], args[16]]

        self.ground_entity_num = args[17]

        self.legs_timer = args[18]
        self.legs_anim = args[19]

        self.torso_timer = args[20]
        self.torso_anim = args[21]

        self.movement_dir = args[22]

        self.grapple_point = [args[23], args[24], args[25]]

        self.e_flags = args[26]

        self.event_sequence = args[27]
        self.events = [args[28], args[29]]
        self.event_parms = [args[30], args[31]]

        self.external_event = args[32]
        self.external_event_parm = args[33]
        self.external_event_time = args[34]

        self.client_num = args[35]
        self.weapon = args[36]
        self.weapon_state = args[37]

        self.view_angles = [args[38], args[39], args[40]]
        self.view_height = args[41]

        self.damage_event = args[42]
        self.damage_yaw = args[43]
        self.damage_pitch = args[44]
        self.damage_count = args[45]

        # stats[13] is usercmd_t in demoes? to be verified
        # stats[12] is timer running verify
        # stats[7] + stats[8] is current time (sec/ms?) verify
        self.stats = []

        self.persistant = []
        self.powerups = []
        self.ammo = []
        for i in range(16):
            self.stats.append(args[46 + i])
            self.persistant.append(args[62 + i])
            self.powerups.append(args[78 + i])
            self.ammo.append(args[94 + i])

        self.generic_1 = args[110]
        self.loop_sound = args[111]
        self.jumppad_ent = args[112]

        self.ping = args[113]
        self.pmove_framecount = args[114]
        self.jumppad_frame = args[115]
        self.entity_event_sequence = args[116]
