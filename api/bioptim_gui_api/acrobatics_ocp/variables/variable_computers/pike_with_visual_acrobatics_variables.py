import numpy as np

from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.pike_acrobatics_variables import (
    PikeAcrobaticsVariables,
)


class PikeAcrobaticsWithVisualVariables(PikeAcrobaticsVariables):
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
    ZrotRightLowerArm = 12
    XrotRightLowerArm = 13
    ZrotLeftUpperArm = 14
    YrotLeftUpperArm = 15
    ZrotLeftLowerArm = 16
    XrotLeftLowerArm = 17
    XrotUpperLegs = 18
    YrotUpperLegs = 19

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
        "Right lower arm rotation Z",
        "Right lower arm rotation X",
        "Left upper arm rotation Z",
        "Left upper arm rotation Y",
        "Left lower arm rotation Z",
        "Left lower arm rotation X",
        "Upper legs rotation X",
        "Upper legs rotation Y",
    ]

    nb_q, nb_qdot, nb_tau = 20, 20, 14

    arm_dofs = [
        ZrotRightUpperArm,
        YrotRightUpperArm,
        ZrotRightLowerArm,
        XrotRightLowerArm,
        ZrotLeftUpperArm,
        YrotLeftUpperArm,
        ZrotLeftLowerArm,
        XrotLeftLowerArm,
    ]
    shoulder_dofs = [
        ZrotRightUpperArm,
        YrotRightUpperArm,
        ZrotLeftUpperArm,
        YrotLeftUpperArm,
    ]
    elbow_dofs = [
        ZrotRightLowerArm,
        XrotRightLowerArm,
        ZrotLeftLowerArm,
        XrotLeftLowerArm,
    ]

    legs_xdofs = [XrotUpperLegs]

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
            [-1.8] * 3,
            [-2.65] * 3,
            [-2.0] * 3,
            [-3.0] * 3,
            [-1.1] * 3,
            [-2.65] * 3,
            [-2.7] * 3,
            [-0.1] * 3,
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
            [1.1] * 3,
            [0.0] * 3,
            [0.65] * 3,
            [0.05] * 3,
            [1.8] * 3,
            [0.0] * 3,
            [0.3] * 3,
            [0.1] * 3,
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
