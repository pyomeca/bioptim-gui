from fastapi import APIRouter, HTTPException

from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_requests import (
    CollisionConstraintRequest,
    NbHalfTwistsRequest,
    NbSomersaultsRequest,
    PositionRequest,
    VisualCriteriaRequest,
    WithSpineRequest,
)
from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_responses import (
    NbSomersaultsResponse,
    PositionResponse,
    VisualCriteriaResponse,
    CollisionConstraintResponse,
    WithSpineResponse,
)
from bioptim_gui_api.acrobatics_ocp.misc.phase_updating import update_phase_info


class AcrobaticsPhaseModifiers:
    # endpoints that modifies greatly the phases (number, objectives, constraints, variables)
    # that uses the update_phase_info function
    def __init__(self, data):
        self.data = data
        self.router = None

    def register(self, route: APIRouter) -> None:
        self.router = route
        # register additional endpoints
        self.register_put_nb_somersaults()
        self.register_put_nb_half_twists()
        self.register_put_position()
        self.register_put_with_visual_criteria()
        self.register_put_collision_constraint()
        self.register_put_with_spine()

    def register_put_nb_somersaults(self):
        @self.router.put("/nb_somersaults", response_model=NbSomersaultsResponse)
        def update_nb_somersaults(nb_somersaults: NbSomersaultsRequest):
            """
            Append or pop the half_twists list
            Update the number of somersaults of the acrobatics ocp
            Update the phase info of the acrobatics ocp accordingly
            """
            nb_max_somersaults = 5
            new_nb_somersaults = nb_somersaults.nb_somersaults

            # error handling
            old_value = self.data.read_data("nb_somersaults")
            if new_nb_somersaults <= 0 or new_nb_somersaults > nb_max_somersaults:
                raise HTTPException(status_code=400, detail="nb_somersaults must be positive")

            # updating data
            data = self.data.read_data()

            additional_twists = [0] * (new_nb_somersaults - old_value)
            filtered_twists = data["nb_half_twists"][:new_nb_somersaults]
            updated_half_twists = filtered_twists + additional_twists

            self.data.update_data("nb_somersaults", new_nb_somersaults)
            self.data.update_data("nb_half_twists", updated_half_twists)

            # 1 somersault tuck/pike are not allowed, set the position to straight
            if new_nb_somersaults == 1 and data["position"] != "straight":
                self.data.update_data("position", "straight")

            update_phase_info()
            data = self.data.read_data()
            return NbSomersaultsResponse(
                nb_somersaults=data["nb_somersaults"],
                nb_half_twists=data["nb_half_twists"],
                position=data["position"],
                phases_info=data["phases_info"],
                dof_names=data["dof_names"],
            )

    def register_put_nb_half_twists(self):
        @self.router.put("/nb_half_twists/{somersault_index}", response_model=list)
        def put_nb_half_twist(somersault_index: int, half_twists_request: NbHalfTwistsRequest):
            # error handling
            if half_twists_request.nb_half_twists < 0:
                raise HTTPException(status_code=400, detail="nb_half_twists must be positive or zero")

            # updating data
            half_twists = self.data.read_data("nb_half_twists")
            half_twists[somersault_index] = half_twists_request.nb_half_twists
            self.data.update_data("nb_half_twists", half_twists)

            phases = update_phase_info()
            return phases

    def register_put_position(self):
        @self.router.put("/position", response_model=PositionResponse)
        def put_position(position: PositionRequest):
            new_value = position.position.value

            # error handling
            old_value = self.data.read_data("position")
            if old_value == new_value:
                raise HTTPException(
                    status_code=304,
                    detail=f"position is already {position}",
                )

            # updating data
            self.data.update_data("position", new_value)
            nb_somersaults = self.data.read_data("nb_somersaults")

            # 1 somersault tuck/pike are not allowed, set the nb_somersault to 2
            if old_value == "straight" and nb_somersaults == 1:
                half_twists = self.data.read_data("nb_half_twists") + [0]
                self.data.update_data("nb_somersaults", 2)
                self.data.update_data("nb_half_twists", half_twists)

            update_phase_info()
            data = self.data.read_data()
            return PositionResponse(
                nb_somersaults=data["nb_somersaults"],
                nb_half_twists=data["nb_half_twists"],
                position=data["position"],
                phases_info=data["phases_info"],
                dof_names=data["dof_names"],
            )

    def register_put_with_visual_criteria(self):
        @self.router.put("/with_visual_criteria", response_model=VisualCriteriaResponse)
        def put_with_visual_criteria(visual_criteria: VisualCriteriaRequest):
            new_value = visual_criteria.with_visual_criteria

            # error handling
            old_value = self.data.read_data("with_visual_criteria")
            if old_value == new_value:
                raise HTTPException(
                    status_code=304,
                    detail=f"with_visual_criteria is already {old_value}",
                )

            # updating data
            self.data.update_data("with_visual_criteria", new_value)

            update_phase_info()
            data = self.data.read_data()
            return VisualCriteriaResponse(
                with_visual_criteria=data["with_visual_criteria"],
                phases_info=data["phases_info"],
                dof_names=data["dof_names"],
            )

    def register_put_collision_constraint(self):
        @self.router.put("/collision_constraint", response_model=CollisionConstraintResponse)
        def put_collision_constraint(collision_constraint: CollisionConstraintRequest):
            new_value = collision_constraint.collision_constraint

            # error handling
            old_value = self.data.read_data("collision_constraint")
            if old_value == new_value:
                raise HTTPException(
                    status_code=304,
                    detail=f"collision_constraint is already {old_value}",
                )

            # updating data
            self.data.update_data("collision_constraint", new_value)

            update_phase_info()
            data = self.data.read_data()
            return CollisionConstraintResponse(
                collision_constraint=data["collision_constraint"],
                phases_info=data["phases_info"],
            )

    def register_put_with_spine(self):
        @self.router.put("/with_spine", response_model=WithSpineResponse)
        def put_with_spine(with_spine: WithSpineRequest):
            new_value = with_spine.with_spine

            # error handling
            old_value = self.data.read_data("with_spine")
            if old_value == new_value:
                raise HTTPException(
                    status_code=304,
                    detail=f"with_spine is already {old_value}",
                )

            # updating data
            self.data.update_data("with_spine", new_value)
            if new_value:
                self.data.update_data("dynamics", "JOINTS_ACCELERATION_DRIVEN")
            else:
                self.data.update_data("dynamics", "TORQUE_DRIVEN")

            update_phase_info()
            data = self.data.read_data()
            return WithSpineResponse(
                with_spine=data["with_spine"],
                dynamics=data["dynamics"],
                phases_info=data["phases_info"],
                dof_names=data["dof_names"],
            )
