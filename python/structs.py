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
