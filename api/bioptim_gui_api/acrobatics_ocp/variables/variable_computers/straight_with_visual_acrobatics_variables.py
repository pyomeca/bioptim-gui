import numpy as np

from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.straight_acrobatics_variables import (
    StraightAcrobaticsVariables,
)


class StraightAcrobaticsWithVisualVariables(StraightAcrobaticsVariables):
    X = 0
    Y = 1
    Z = 2
    Xrot = 3
    Yrot = 4
    Zrot = 5
    ZrotHead = 6
    XrotHead = 7
    ZrotEyes = 8
    XrotEyes = 9
    ZrotRightUpperArm = 10
    YrotRightUpperArm = 11
    ZrotLeftUpperArm = 12
    YrotLeftUpperArm = 13

    dofs = [
        "Pelvis translation X",
        "Pelvis translation Y",
        "Pelvis translation Z",
        "Pelvis rotation X",
        "Pelvis rotation Y",
        "Pelvis rotation Z",
        "Head rotation Z",
        "Head rotation X",
        "Eyes rotation Z",
        "Eyes rotation X",
        "Right upper arm rotation Z",
        "Right upper arm rotation Y",
        "Left upper arm rotation Z",
        "Left upper arm rotation Y",
    ]

    nb_q, nb_qdot, nb_tau = 14, 14, 10

    arm_dofs = [
        ZrotRightUpperArm,
        YrotRightUpperArm,
        ZrotLeftUpperArm,
        YrotLeftUpperArm,
    ]

    shoulder_dofs = [
        ZrotRightUpperArm,
        YrotRightUpperArm,
        ZrotLeftUpperArm,
        YrotLeftUpperArm,
    ]

    q_min_bounds = np.array(
        [
            [-1] * 3,
            [-1] * 3,
            [-0.1] * 3,
            [0] * 3,
            [-np.pi / 4] * 3,
            [0] * 3,
            [-np.pi / 3] * 3,
            [-70 * np.pi / 180] * 3,
            [-np.pi / 8] * 3,
            [-np.pi / 6] * 3,
            [-0.65] * 3,
            [-0.05] * 3,
            [-2.0] * 3,
            [-3.0] * 3,
        ]
    )

    q_max_bounds = np.array(
        [
            [1] * 3,
            [1] * 3,
            [15] * 3,
            [0] * 3,
            [np.pi / 4] * 3,
            [0] * 3,
            [np.pi / 3] * 3,
            [np.pi / 8] * 3,
            [np.pi / 8] * 3,
            [np.pi / 6] * 3,
            [2.0] * 3,
            [3.0] * 3,
            [0.65] * 3,
            [0.05] * 3,
        ]
    )

    @classmethod
    def get_q_bounds(cls, half_twists: list, prefer_left: bool) -> dict:
        bounds = super().get_q_bounds(half_twists, prefer_left)
        bounds[0]["min"][cls.ZrotHead, 0] = -0.1
        bounds[0]["max"][cls.ZrotHead, 0] = 0.1
        bounds[0]["min"][cls.XrotHead, 0] = -0.1
        bounds[0]["max"][cls.XrotHead, 0] = 0.1
        bounds[0]["min"][cls.ZrotEyes, 0] = -0.1
        bounds[0]["max"][cls.ZrotEyes, 0] = 0.1
        bounds[0]["min"][cls.XrotEyes, 0] = np.pi / 8 - 0.1
        bounds[0]["max"][cls.XrotEyes, 0] = np.pi / 8 + 0.1
        return bounds
