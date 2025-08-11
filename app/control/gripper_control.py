from PyQt5.QtCore import QObject, pyqtSignal
import threading
import time

try:
    import flexivrdk
    FLEXIV_AVAILABLE = True
except ImportError:
    FLEXIV_AVAILABLE = False

class GripperControl(QObject):
    gripper_state_updated = pyqtSignal(object)
    gripper_param_updated = pyqtSignal(object)
    gripper_error = pyqtSignal(str)

    def __init__(self, robot=None, gripper_name=None):
        super().__init__()
        self.robot = robot
        self.gripper_name = gripper_name
        self.gripper = None
        self._running = False
        self._thread = None
        if self.robot and FLEXIV_AVAILABLE:
            try:
                self.gripper = flexivrdk.Gripper(self.robot)
            except Exception as e:
                self.gripper_error.emit(f"Gripper init error: {e}")

    def enable(self, gripper_name=None):
        if not self.gripper:
            self.gripper_error.emit("Gripper not initialized")
            return
        name = gripper_name or self.gripper_name
        try:
            self.gripper.Enable(name)
            self.gripper_param_updated.emit(self.gripper.params())
        except Exception as e:
            self.gripper_error.emit(f"Enable error: {e}")

    def init(self):
        if not self.gripper:
            self.gripper_error.emit("Gripper not initialized")
            return
        try:
            self.gripper.Init()
        except Exception as e:
            self.gripper_error.emit(f"Init error: {e}")

    def move(self, width, vel=0.1, force=20):
        if not self.gripper:
            self.gripper_error.emit("Gripper not initialized")
            return
        try:
            self.gripper.Move(width, vel, force)
        except Exception as e:
            self.gripper_error.emit(f"Move error: {e}")

    def grasp(self, width=0, force=20):
        if not self.gripper:
            self.gripper_error.emit("Gripper not initialized")
            return
        try:
            self.gripper.Grasp(width, force)
        except Exception as e:
            self.gripper_error.emit(f"Grasp error: {e}")

    def stop(self):
        if not self.gripper:
            self.gripper_error.emit("Gripper not initialized")
            return
        try:
            self.gripper.Stop()
        except Exception as e:
            self.gripper_error.emit(f"Stop error: {e}")

    def start_state_monitor(self, interval=1.0):
        if not self.gripper:
            self.gripper_error.emit("Gripper not initialized")
            return
        self._running = True
        self._thread = threading.Thread(target=self._state_monitor_loop, args=(interval,))
        self._thread.daemon = True
        self._thread.start()

    def stop_state_monitor(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def _state_monitor_loop(self, interval):
        while self._running:
            try:
                state = self.gripper.states()
                self.gripper_state_updated.emit(state)
            except Exception as e:
                self.gripper_error.emit(f"State monitor error: {e}")
            time.sleep(interval)

    def set_robot(self, robot):
        self.robot = robot
        if self.robot and FLEXIV_AVAILABLE:
            try:
                self.gripper = flexivrdk.Gripper(self.robot)
            except Exception as e:
                self.gripper_error.emit(f"Gripper init error: {e}") 