import numpy as np
import pytest

from bioptim_gui_api.acrobatics_ocp.misc.acrobatics_utils import acrobatics_phase_names
from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.pike_acrobatics_variables import (
    PikeAcrobaticsVariables,
)
from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.pike_with_visual_acrobatics_variables import (
    PikeAcrobaticsWithVisualVariables,
)
from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.straight_acrobatics_variables import (
    StraightAcrobaticsVariables,
)
from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.straight_with_visual_acrobatics_variables import (
    StraightAcrobaticsWithVisualVariables,
)
from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.tuck_acrobatics_variables import (
    TuckAcrobaticsVariables,
)
from bioptim_gui_api.acrobatics_ocp.variables.variable_computers.tuck_with_visual_acrobatics_variables import (
    TuckAcrobaticsWithVisualVariables,
)
from tests.acrobatics_ocp.variables.variable_computers.pike_acrobatics_variables import (
    PikeAcrobaticsVariables as BasePikeAcrobaticsVariables,
)
from tests.acrobatics_ocp.variables.variable_computers.pike_with_visual_acrobatics_variables import (
    PikeAcrobaticsWithVisualVariables as BasePikeAcrobaticsWithVisualVariables,
)
from tests.acrobatics_ocp.variables.variable_computers.straight_acrobatics_variables import (
    StraightAcrobaticsVariables as BaseStraightAcrobaticsVariables,
)
from tests.acrobatics_ocp.variables.variable_computers.straight_with_visual_acrobatics_variables import (
    StraightAcrobaticsWithVisualVariables as BaseStraightAcrobaticsWithVisualVariables,
)
from tests.acrobatics_ocp.variables.variable_computers.tuck_acrobatics_variables import (
    TuckAcrobaticsVariables as BaseTuckAcrobaticsVariables,
)
from tests.acrobatics_ocp.variables.variable_computers.tuck_with_visual_acrobatics_variables import (
    TuckAcrobaticsWithVisualVariables as BaseTuckAcrobaticsWithVisualVariables,
)


@pytest.mark.parametrize(
    ("variable_compute", "baseline", "position"),
    [
        (StraightAcrobaticsVariables, BaseStraightAcrobaticsVariables, "straight"),
        (PikeAcrobaticsVariables, BasePikeAcrobaticsVariables, "pike"),
        (TuckAcrobaticsVariables, BaseTuckAcrobaticsVariables, "tuck"),
        (StraightAcrobaticsWithVisualVariables, BaseStraightAcrobaticsWithVisualVariables, "straight"),
        (PikeAcrobaticsWithVisualVariables, BasePikeAcrobaticsWithVisualVariables, "pike"),
        (TuckAcrobaticsWithVisualVariables, BaseTuckAcrobaticsWithVisualVariables, "tuck"),
    ],
)
@pytest.mark.parametrize("prefer_left", [True, False])
@pytest.mark.parametrize(
    "half_twist",
    [
        [0, 0],
        [0, 1],
        [1, 0],
        [1, 1],
        [0, 0, 0],
        [0, 0, 1],
        [0, 1, 0],
        [0, 1, 1],
        [1, 0, 0],
        [1, 0, 1],
        [1, 1, 0],
        [1, 1, 1],
    ],
)
def test_qdot_bounds(variable_compute, baseline, position, prefer_left, half_twist):
    nb_phases = len(acrobatics_phase_names(len(half_twist), position, half_twist))
    expected = baseline.get_qdot_bounds(nb_phases, 2, prefer_left)
    actual = variable_compute.get_qdot_bounds(nb_phases, 2, prefer_left)

    assert len(expected) == len(actual)

    for i in range(len(expected)):
        assert np.allclose(expected[i]["min"], actual[i]["min"])
        assert np.allclose(expected[i]["max"], actual[i]["max"])
