import os
import logging

LOG_FILENAME = "logs/output.log"

# Only called once
def CL_InitCGame():
    with open("test", "w") as f:
        f.write("test")
    os.makedirs(os.path.dirname(LOG_FILENAME), exist_ok=True)
    logging.basicConfig(filename=LOG_FILENAME, filemode='a', format='%(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


# Called every frame
def CL_CreateCmd(server_time, angles_1, angles_2, angles_3, buttons, weapon, forwardmove, rightmove, upmove):
    logging.debug(f"{server_time} {angles_1} {angles_2} {angles_3} {buttons} {weapon} {forwardmove} {rightmove} {upmove}")


if __name__ == "__main__":
    LOG_FILENAME = "../logs/output.log"
    CL_InitCGame()
    CL_CreateCmd(0, 0, 0, 0, 0, 0, 0, 0, 0)
