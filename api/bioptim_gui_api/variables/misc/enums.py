from enum import Enum


class Dynamics(str, Enum):
    TORQUE_DRIVEN = "TORQUE_DRIVEN"
    JOINTS_ACCELERATION_DRIVEN = "JOINTS_ACCELERATION_DRIVEN"
