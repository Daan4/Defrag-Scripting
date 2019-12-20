# Data container classes to mirror the C structs


class BaseStruct:
    def __iter__(self):
        for _, v in self.__dict__.items():
            yield v

    def __repr__(self):
        return " ".join([str(v) for _, v in self.__dict__.items()])


class usercmd_t(BaseStruct):
    def __init__(self, server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove):
        self.server_time = server_time
        self.angles_1 = angles_1
        self.angles_2 = angles_2
        self.angles_3 = angles_3
        self.buttons = buttons
        self.weapon = weapon
        self.forwardmove = forwardmove
        self.rightmove = rightmove
        self.upmove = upmove


class playerstate_t(BaseStruct):
    def __init__(self, *args):
        self.command_time = args[0]
        self.pm_type = args[1]
        self.bob_cycle = args[2]
        self.pm_flags = args[3]
        self.pm_time = args[4]

        self.origin_1 = args[5]
        self.origin_2 = args[6]
        self.origin_3 = args[7]
        self.velocity_1 = args[8]
        self.velocity_2 = args[9]
        self.velocity_3 = args[10]
        self.weapon_time = args[11]
        self.gravity = args[12]
        self.speed = args[13]
        self.delta_angles_1 = args[14]
        self.delta_angles_2 = args[15]
        self.delta_angles_3 = args[16]

        self.ground_entity_num = args[17]

        self.legs_timer = args[18]
        self.legs_anim = args[19]

        self.torso_timer = args[20]
        self.torso_anim = args[21]

        self.movement_dir = args[22]

        self.grapple_point_1 = args[23]
        self.grapple_point_2 = args[24]
        self.grapple_point_3 = args[25]

        self.e_flags = args[26]

        self.event_sequence = args[27]
        self.events = [args[28], args[29]]
        self.event_parms = [args[30], args[31]]
        #todo continue?


