from enum import Enum


class RobotState(Enum):
    """机器人状态枚举"""
    DISCONNECTED = "disconnected"
    CONNECTED = "connected"
    IDLE = "idle"
    ENABLED = "enabled"
    MOVING = "moving"
    FAULT = "fault"
    ESTOP = "estop"


class GripperState(Enum):
    """夹爪状态枚举"""
    OPEN = "open"
    CLOSED = "closed"
    MOVING = "moving"
    FAULT = "fault"


class MotionPrimitive(Enum):
    """运动原语枚举"""
    JOINT_MOVE = "joint_move"
    LINEAR_MOVE = "linear_move"
    TEACHING = "teaching"
    PLAN_EXECUTION = "plan_execution"