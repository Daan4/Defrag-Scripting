import os


def callback():
    if not os.path.isfile("test"):
        with open("test", "w") as f:
            f.write("TEST SUCCESS")
