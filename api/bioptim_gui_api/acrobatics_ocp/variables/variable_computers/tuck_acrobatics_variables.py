import numpy as np

from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.pike_acrobatics_variables import (
    PikeAcrobaticsVariables,
)


class TuckAcrobaticsVariables(PikeAcrobaticsVariables):
    X = 0
    Y = 1
    Z = 2
    Xrot = 3
    Yrot = 4
    Zrot = 5
    ZrotRightUpperArm = 6
    YrotRightUpperArm = 7
    ZrotRightLowerArm = 8
    XrotRightLowerArm = 9
    ZrotLeftUpperArm = 10
    YrotLeftUpperArm = 11
    ZrotLeftLowerArm = 12
    XrotLeftLowerArm = 13
    XrotUpperLegs = 14
    YrotUpperLegs = 15
    XrotLowerLegs = 16

    dofs = [
        "Pelvis translation X",
        "Pelvis translation Y",
        "Pelvis translation Z",
        "Pelvis rotation X",
        "Pelvis rotation Y",
        "Pelvis rotation Z",
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
        "Lower legs rotation X",
    ]

    nb_q, nb_qdot, nb_tau = 17, 17, 11

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

    legs_xdofs = [XrotUpperLegs, XrotLowerLegs]

    q_min_bounds = np.array(
        [
            [-1] * 3,
            [-1] * 3,
            [-0.1] * 3,
            [0] * 3,
            [-np.pi / 4] * 3,
            [0] * 3,
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
            [-np.pi] * 3,
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
            [np.pi] * 3,
        ]
    )

    @classmethod
    def get_q_bounds(cls, half_twists: list, prefer_left: bool) -> dict:
        x_bounds = super().get_q_bounds(half_twists, prefer_left)
        nb_phases = len(x_bounds)

        # the number of tuck is at least 1, every twists that are not the
        # first phase or last phase before landing have a tuck phase
        n_tucks = sum(np.array(half_twists[1:-1]) > 0) + 1

        # every tuck phases are 4 phases apart
        tuck_phase_idx = np.array([i * 4 for i in range(n_tucks)])

        # if the first phase is not a pike (if it is a twist) the tuck phases
        # are shifted by 1
        if half_twists[0] > 0:
            tuck_phase_idx += 1

        for i in range(nb_phases):
            x_bounds[i]["min"][cls.XrotLowerLegs, :] = -0.15
            x_bounds[i]["max"][cls.XrotLowerLegs, :] = 0.15

        for idx in tuck_phase_idx:
            # tucking
            x_bounds[idx]["min"][cls.XrotLowerLegs, 0] = -0.2
            x_bounds[idx]["max"][cls.XrotLowerLegs, 0] = 0.2
            x_bounds[idx]["min"][cls.XrotLowerLegs, 1] = -0.2
            x_bounds[idx]["max"][cls.XrotLowerLegs, 1] = 2.4 + 0.2
            x_bounds[idx]["min"][cls.XrotLowerLegs, 2] = 2.4 - 0.2
            x_bounds[idx]["max"][cls.XrotLowerLegs, 2] = 2.4 + 0.2

            # somersaulting in tuck
            x_bounds[idx + 1]["min"][cls.XrotLowerLegs, :] = 2.4 - 0.2
            x_bounds[idx + 1]["max"][cls.XrotLowerLegs, :] = 2.4 + 0.2

            # kick out
            x_bounds[idx + 2]["min"][cls.XrotLowerLegs, 0] = 2.4 - 0.21
            x_bounds[idx + 2]["max"][cls.XrotLowerLegs, 0] = 2.4 + 0.21
            x_bounds[idx + 2]["min"][cls.XrotLowerLegs, 1] = -0.21
            x_bounds[idx + 2]["max"][cls.XrotLowerLegs, 1] = 2.4 + 0.21

        return x_bounds
