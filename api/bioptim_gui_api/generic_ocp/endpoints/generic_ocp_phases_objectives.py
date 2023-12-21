from fastapi import APIRouter

from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_penalties import GenericOCPPenaltyRouter
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_requests import (
    ObjectiveTypeRequest,
    WeightRequest,
    ObjectiveFcnRequest,
)
from bioptim_gui_api.generic_ocp.endpoints.generic_ocp_responses import (
    WeightResponse,
)
from bioptim_gui_api.penalty.misc.penalty_config import DefaultPenaltyConfig
from bioptim_gui_api.penalty.misc.penalty_utils import obj_arguments


class GenericOCPObjectiveRouter(GenericOCPPenaltyRouter):
    def __init__(self, data):
        super().__init__(data, "objectives")
        self.arg_getter = obj_arguments
        self.default = DefaultPenaltyConfig.default_objective

    def register(self, route: APIRouter) -> None:
        super().register(route)
        self.register_put_objective_type()
        self.register_put_objective_weight()
        self.register_put_objective_weight_maximize()
        self.register_put_objective_weight_minimize()

    def register_put_penalty_type(self):
        @self.router.put("/{phase_index}/objectives/{objective_index}/penalty_type", response_model=dict)
        def put_objective_penalty_type(phase_index: int, objective_index: int, penalty_type: ObjectiveFcnRequest):
            penalty_type_value = penalty_type.penalty_type
            phases_info = self.data.read_data("phases_info")

            phases_info[phase_index]["objectives"][objective_index]["penalty_type"] = penalty_type_value

            objective_type = phases_info[phase_index]["objectives"][objective_index]["objective_type"]
            weight = phases_info[phase_index]["objectives"][objective_index]["weight"]

            if weight > 0:
                penalty_type_value = DefaultPenaltyConfig.min_to_original_dict[penalty_type_value]
            else:
                penalty_type_value = DefaultPenaltyConfig.max_to_original_dict[penalty_type_value]

            try:
                arguments = obj_arguments(objective_type=objective_type, penalty_type=penalty_type_value)
            except AttributeError:
                other_objective_type = "lagrange" if objective_type == "mayer" else "mayer"
                phases_info[phase_index]["objectives"][objective_index]["objective_type"] = other_objective_type
                arguments = obj_arguments(objective_type=other_objective_type, penalty_type=penalty_type_value)

            phases_info[phase_index]["objectives"][objective_index]["arguments"] = arguments

            self.data.update_data("phases_info", phases_info)

            data = self.data.read_data()
            return data["phases_info"][phase_index]["objectives"][objective_index]

    def register_get_phase_penalty_list(self):
        @self.router.get("/{phase_index}/objectives/{objective_index}", response_model=list)
        def get_objective_dropdown_list(phase_index: int, objective_index: int):
            phases_info = self.data.read_data("phases_info")
            objective = phases_info[phase_index]["objectives"][objective_index]
            weight = objective["weight"]

            if weight > 0:
                return list(DefaultPenaltyConfig.min_to_original_dict.keys())
            return list(DefaultPenaltyConfig.max_to_original_dict.keys())

    def register_put_objective_type(self):
        @self.router.put("/{phase_index}/objectives/{objective_index}/objective_type", response_model=dict)
        def put_objective_type(phase_index: int, objective_index: int, objective_type: ObjectiveTypeRequest):
            phases_info = self.data.read_data("phases_info")
            phases_info[phase_index]["objectives"][objective_index][
                "objective_type"
            ] = objective_type.objective_type.value

            objective_type_value = objective_type.objective_type.value
            penalty_type = phases_info[phase_index]["objectives"][objective_index]["penalty_type"]

            if objective_type_value == "lagrange":
                phases_info[phase_index]["objectives"][objective_index]["nodes"] = "all_shooting"

            weight = phases_info[phase_index]["objectives"][objective_index]["weight"]

            if weight > 0:
                penalty_type = DefaultPenaltyConfig.min_to_original_dict[penalty_type]
            else:
                penalty_type = DefaultPenaltyConfig.max_to_original_dict[penalty_type]

            arguments = obj_arguments(objective_type_value, penalty_type)

            phases_info[phase_index]["objectives"][objective_index]["arguments"] = arguments

            self.data.update_data("phases_info", phases_info)
            data = self.data.read_data()
            return data["phases_info"][phase_index]["objectives"][objective_index]

    def register_put_objective_weight(self):
        @self.router.put("/{phase_index}/objectives/{objective_index}/weight", response_model=WeightResponse)
        def put_objective_weight(phase_index: int, objective_index: int, weight: WeightRequest):
            phases_info = self.data.read_data("phases_info")

            old_weight = phases_info[phase_index]["objectives"][objective_index]["weight"]
            new_weight = weight.weight if old_weight > 0 else -weight.weight

            phases_info[phase_index]["objectives"][objective_index]["weight"] = new_weight
            self.data.update_data("phases_info", phases_info)
            return WeightResponse(weight=new_weight)

    def register_put_objective_weight_maximize(self):
        @self.router.put("/{phase_index}/objectives/{objective_index}/weight/maximize", response_model=dict)
        def put_objective_weight_maximize(phase_index: int, objective_index: int):
            phases_info = self.data.read_data("phases_info")
            old_weight = phases_info[phase_index]["objectives"][objective_index]["weight"]
            new_weight = -abs(old_weight)

            phases_info[phase_index]["objectives"][objective_index]["weight"] = new_weight
            penalty_type = phases_info[phase_index]["objectives"][objective_index]["penalty_type"]

            if old_weight > 0:
                phases_info[phase_index]["objectives"][objective_index][
                    "penalty_type"
                ] = DefaultPenaltyConfig.min_to_max(penalty_type)

            self.data.update_data("phases_info", phases_info)
            return phases_info[phase_index]["objectives"][objective_index]

    def register_put_objective_weight_minimize(self):
        @self.router.put("/{phase_index}/objectives/{objective_index}/weight/minimize", response_model=dict)
        def put_objective_weight_minimize(phase_index: int, objective_index: int):
            phases_info = self.data.read_data("phases_info")
            old_weight = phases_info[phase_index]["objectives"][objective_index]["weight"]
            new_weight = abs(old_weight)

            phases_info[phase_index]["objectives"][objective_index]["weight"] = new_weight
            penalty_type = phases_info[phase_index]["objectives"][objective_index]["penalty_type"]

            if old_weight < 0:
                phases_info[phase_index]["objectives"][objective_index][
                    "penalty_type"
                ] = DefaultPenaltyConfig.max_to_min(penalty_type)

            self.data.update_data("phases_info", phases_info)
            return phases_info[phase_index]["objectives"][objective_index]
