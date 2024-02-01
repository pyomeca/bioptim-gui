from typing import NamedTuple

from pydantic import BaseModel

from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_requests import (
    FinalTimeMarginRequest,
    FinalTimeRequest,
    PreferredTwistSideRequest,
    SportTypeRequest,
    NbSomersaultsRequest,
    PositionRequest,
    VisualCriteriaRequest,
    CollisionConstraintRequest,
    WithSpineRequest,
)
from bioptim_gui_api.acrobatics_ocp.misc.enums import Position
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_requests import PhaseDurationRequest, DynamicsRequest
from bioptim_gui_api.variables.misc.enums import Dynamics


class NbSomersaultsResponse(NbSomersaultsRequest):
    nb_half_twists: list[int]
    position: Position
    phases_info: list[dict]
    dof_names: list[str]


class PositionResponse(PositionRequest):
    nb_somersaults: int
    nb_half_twists: list[int]
    phases_info: list[dict]
    dof_names: list[str]


class FinalTimeResponse(FinalTimeRequest):
    new_phase_duration: float


class FinalTimeMarginResponse(FinalTimeMarginRequest):
    pass


class SportTypeResponse(SportTypeRequest):
    pass


class PreferredTwistSideResponse(PreferredTwistSideRequest):
    pass


class VisualCriteriaResponse(VisualCriteriaRequest):
    phases_info: list[dict]
    dof_names: list[str]


class CollisionConstraintResponse(CollisionConstraintRequest):
    phases_info: list[dict]


class AcrobaticsDynamicResponse(DynamicsRequest):
    phases_info: list[dict]


class WithSpineResponse(WithSpineRequest):
    dynamics: Dynamics
    phases_info: list[dict]
    dof_names: list[str]


class AcrobaticPhaseDurationResponse(PhaseDurationRequest):
    new_final_time: float


class NewGeneratedBioMod(NamedTuple):
    new_model: str
    new_model_path: str


class CodeGenerationResponse(BaseModel):
    generated_code: str
    new_models: list[NewGeneratedBioMod]
