from enum import Enum


class ObjectiveType(str, Enum):
    MAYER = "mayer"
    LAGRANGE = "lagrange"


class Node(str, Enum):
    START = "start"
    MID = "mid"
    INTERMEDIATES = "intermediates"
    PENULTIMATE = "penultimate"
    END = "end"
    ALL = "all"
    ALL_SHOOTING = "all_shooting"
    TRANSITION = "transition"
    MULTINODES = "multinodes"
    DEFAULT = "default"
    ALL_3 = "all[3:]"
    ALL_3_ = "all[:-3]"
