import g
import logging
from abc import ABCMeta, abstractmethod


class BaseScript:
    """Contains common core functionality. Scripts should inherit from BaseScript's children instead."""
    def __init__(self):
        self.running = False  # True if script is running
        self.waiting = False  # True if script is waiting
        self.prev_waiting = False  # Waiting state of previous frame, used to detect script finish in the callback
        self.wait_script = None  # Instance of the script that the current script is waiting on, or None
        self.stop_condition = None  # A function which auto-stops the script if it evaluates to True
        self.autostart = False

    def on_start(self, *args, **kwargs):
        """Called when script is started by startscript console command"""
        pass

    def on_stop(self):
        """Called when script is stopped by stopscript console command"""
        pass

    def do(self, script_class, stop_condition=None, *args, **kwargs):
        """Start another script, and if a stop_condition is given wait for it to finish."""
        for instance in g.script_instances:
            if script_class is instance.__class__:
                if stop_condition is not None:
                    self.wait(instance)
                instance.CL_StartScript(script_class.__name__, stop_condition, *args, **kwargs)
                return instance

    def wait(self, instance):
        """Wait on instance to finish"""
        self.wait_script = instance
        self.prev_waiting = self.waiting
        self.waiting = True

    def wait_done(self):
        """Check if the wait finished this frame"""
        return self.prev_waiting and not self.waiting

    def on_wait(self):
        """Called on every run call to see if we are still waiting"""
        if not self.wait_script.running:
            self.wait_script = None
            self.prev_waiting = self.waiting
            self.waiting = False

    def run(self, callback, *args, **kwargs):
        if self.waiting:
            self.on_wait()

        if callback == self.CL_StartScript.__name__:
            return self.CL_StartScript(*args, **kwargs)
        elif self.running and not self.waiting:
            if not self.stop_condition():
                # Fire the callback
                return getattr(self, callback)(*args, **kwargs)
            else:
                self.CL_StopScript()
        elif self.waiting and callback == self.CL_StopScript.__name__:
            # Still allow script to be stopped while waiting
            return self.CL_StopScript(*args, **kwargs)

        # Return the original args if the callback wasn't fired
        if len(args) == 1:
            return args[0]
        else:
            return args

    def CL_CreateCmd(self, cmd):
        return cmd

    def CL_StartScript(self, script_class_name=None, stop_condition=None, *args, **kwargs):
        if script_class_name is None:
            script_class_name = self.__class__.__name__
        if script_class_name.lower() == self.__class__.__name__.lower() and not self.running:
            logging.debug(f"Starting script \"{script_class_name}\" with args \"{args}\" and kwargs \"{kwargs}\"")
            self.on_start(*args, **kwargs)
            if stop_condition is None:
                stop_condition = lambda: False
            self.stop_condition = stop_condition
            self.running = True
            return True
        return False

    def CL_StopScript(self, script_class_name=None):
        if script_class_name is None:
            script_class_name = self.__class__.__name__
        if script_class_name.lower() == self.__class__.__name__.lower() and self.running:
            logging.debug(f"Stopping script \"{script_class_name}\"")
            self.on_stop()
            self.wait_script = None
            self.waiting = False
            self.prev_waiting = False
            self.running = False
            return True
        return False

    def CL_ParseSnapshot(self, _ps):
        pass


class BasicScript(BaseScript):
    """Like BaseScript"""
    def __init__(self):
        super().__init__()


class StartScript(BaseScript):
    """Start scripts are called first, before any of the other registered scripts.
    Autostarts by default
    """
    def __init__(self):
        super().__init__()
        self.autostart = True


class FinalScript(BaseScript):
    """Final scripts are called last, after any of the other registered scripts.
    Autostarts by default"""
    def __init__(self):
        super().__init__()
        self.autostart = True


class BotScript(BaseScript, metaclass=ABCMeta):
    """Same as BaseScript, but these are called before BaseScripts
    This allows any BaseScript started in a BotScript to start in the same frame.
    Implements CL_CreateCmd and uses a statemachine to execute a sequence of BaseScripts
    The sequence should be initialized in init_script_sequence which has to be implemented by the subclass
    """
    def __init__(self):
        super().__init__()
        self.script_sequence = []
        self.current_script = 0
        self.init_script_sequence()
        self.autostart = False

    def add_script(self, script_class, stop_condition=None, *args, **kwargs):
        """Register a script in the script sequence"""
        if stop_condition is None:
            stop_condition = lambda: False
        self.script_sequence.append([script_class, stop_condition, args, kwargs])

    def CL_CreateCmd(self, cmd):
        if self.wait_done():
            self.current_script += 1

        if self.current_script == len(self.script_sequence):
            self.CL_StopScript()
        else:
            script_class, stop_condition, args, kwargs = self.script_sequence[self.current_script]
            self.do(script_class, stop_condition, *args, **kwargs)
        return cmd

    def on_start(self, *args, **kwargs):
        self.current_script = 0

    @abstractmethod
    def init_script_sequence(self):
        pass
