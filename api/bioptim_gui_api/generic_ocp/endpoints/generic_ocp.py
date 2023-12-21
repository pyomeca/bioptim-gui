from fastapi import APIRouter, HTTPException

from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_code_generation import (
    router as code_generation_router,
)
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_phases import (
    GenericPhaseRouter,
)
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_phases_constraints import GenericOCPConstraintRouter
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_phases_objectives import GenericOCPObjectiveRouter
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_phases_variables import (
    GenericControlVariableRouter,
    GenericStateVariableRouter,
)
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_requests import (
    ModelPathRequest,
    NbPhasesRequest,
)
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_responses import (
    ModelPathResponse,
)
from bioptim_gui_api.generic_ocp.misc.generic_ocp_data import GenericOCPData
from bioptim_gui_api.generic_ocp.misc.generic_ocp_utils import add_phase_info, remove_phase_info


class GenericOCPBaseFieldRegistrar:
    def __init__(self, data):
        self.data = data
        self.router = None

    def register(self, route: APIRouter) -> None:
        self.router = route

        # register all endpoints
        self.register_get_ocp_data()
        self.register_update_nb_phases()
        self.register_put_model_path()

    def register_get_ocp_data(self) -> None:
        @self.router.get("/", response_model=dict)
        def get_ocp_data():
            data = self.data.read_data()
            return data

    def register_update_nb_phases(self) -> None:
        @self.router.put("/nb_phases", response_model=dict)
        def put_nb_phases(nb_phases: NbPhasesRequest):
            old_value = self.data.read_data("nb_phases")
            new_value = nb_phases.nb_phases
            if new_value < 0:
                raise HTTPException(status_code=400, detail="nb_phases must be positive")

            if new_value > old_value:
                add_phase_info(new_value - old_value)
            elif new_value < old_value:
                remove_phase_info(old_value - new_value)

            self.data.update_data("nb_phases", new_value)

            data = self.data.read_data()
            return data

    def register_put_model_path(self) -> None:
        @self.router.put("/model_path", response_model=ModelPathResponse)
        def put_model_path(model_path: ModelPathRequest):
            self.data.update_data("model_path", model_path.model_path)
            return ModelPathResponse(model_path=model_path.model_path)


router = APIRouter(
    prefix="/generic_ocp",
    tags=["generic_ocp"],
    responses={404: {"description": "Not found"}},
)
GenericOCPBaseFieldRegistrar(GenericOCPData).register(router)

phase_router = APIRouter(
    prefix="/phases_info",
    tags=["phases"],
    responses={404: {"description": "Not found"}},
)
GenericPhaseRouter(GenericOCPData).register(phase_router)
GenericOCPObjectiveRouter(GenericOCPData).register(phase_router)
GenericOCPConstraintRouter(GenericOCPData).register(phase_router)
GenericControlVariableRouter(GenericOCPData).register(phase_router)
GenericStateVariableRouter(GenericOCPData).register(phase_router)

router.include_router(phase_router)

router.include_router(code_generation_router)
