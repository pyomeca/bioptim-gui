class DefaultPenaltyConfig:
    default_objective = {
        "objective_type": "lagrange",
        "penalty_type": "MINIMIZE_STATE",
        "nodes": "all_shooting",
        "quadratic": True,
        "expand": True,
        "target": None,
        "derivative": False,
        "integration_rule": "rectangle_left",
        "multi_thread": False,
        "weight": 1.0,
        "arguments": [
            {"name": "key", "value": "tau", "type": "string"},
            {"name": "index", "value": None, "type": "list"},
        ],
    }

    default_constraint = {
        "penalty_type": "TIME_CONSTRAINT",
        "nodes": "end",
        "quadratic": True,
        "expand": True,
        "target": None,
        "derivative": False,
        "integration_rule": "rectangle_left",
        "multi_thread": False,
        "arguments": [],
    }

    maximizer = {
        "MAXIMIZE_ANGULAR_MOMENTUM": "MINIMIZE_ANGULAR_MOMENTUM",
        "MAXIMIZE_COM_POSITION": "MINIMIZE_COM_POSITION",
        "MAXIMIZE_COM_VELOCITY": "MINIMIZE_COM_VELOCITY",
        "MAXIMIZE_CONTROL": "MINIMIZE_CONTROL",
        "MAXIMIZE_LINEAR_MOMENTUM": "MINIMIZE_LINEAR_MOMENTUM",
        "MAXIMIZE_MARKERS": "MINIMIZE_MARKERS",
        "MAXIMIZE_MARKERS_ACCELERATION": "MINIMIZE_MARKERS_ACCELERATION",
        "MAXIMIZE_MARKERS_VELOCITY": "MINIMIZE_MARKERS_VELOCITY",
        "MAXIMIZE_POWER": "MINIMIZE_POWER",
        "MAXIMIZE_QDDOT": "MINIMIZE_QDDOT",
        "MAXIMIZE_SEGMENT_ROTATION": "MINIMIZE_SEGMENT_ROTATION",
        "MAXIMIZE_SEGMENT_VELOCITY": "MINIMIZE_SEGMENT_VELOCITY",
        "MAXIMIZE_STATE": "MINIMIZE_STATE",
        "MAXIMIZE_TIME": "MINIMIZE_TIME",
    }

    min_to_original_dict = {v: v for v in maximizer.values()} | {
        "PROPORTIONAL_CONTROL": "PROPORTIONAL_CONTROL",
        "PROPORTIONAL_STATE": "PROPORTIONAL_STATE",
        "MINIMIZE_MARKER_DISTANCE": "SUPERIMPOSE_MARKERS",
        "ALIGN_MARKER_WITH_SEGMENT_AXIS": "TRACK_MARKER_WITH_SEGMENT_AXIS",
        "ALIGN_SEGMENT_WITH_CUSTOM_RT": "TRACK_SEGMENT_WITH_CUSTOM_RT",
        "ALIGN_MARKERS_WITH_VECTOR": "TRACK_VECTOR_ORIENTATIONS_FROM_MARKERS",
        "CUSTOM": "CUSTOM",
    }

    max_to_original_dict = maximizer | {
        "PROPORTIONAL_CONTROL": "PROPORTIONAL_CONTROL",
        "PROPORTIONAL_STATE": "PROPORTIONAL_STATE",
        "MAXIMIZE_MARKER_DISTANCE": "SUPERIMPOSE_MARKERS",
        "MARKER_AWAY_FROM_SEGMENT_AXIS": "TRACK_MARKER_WITH_SEGMENT_AXIS",
        "SEGMENT_PERPENDICULAR_WITH_RT": "TRACK_SEGMENT_WITH_CUSTOM_RT",
        "UNALIGN_MARKERS_WITH_VECTOR": "TRACK_VECTOR_ORIENTATIONS_FROM_MARKERS",
        "CUSTOM": "CUSTOM",
    }

    original_to_min_dict = {v: k for k, v in min_to_original_dict.items()}
    original_to_max_dict = {v: k for k, v in max_to_original_dict.items()}

    @classmethod
    def min_to_max(cls, penalty_type):
        return cls.original_to_max_dict[cls.min_to_original_dict[penalty_type]]

    @classmethod
    def max_to_min(cls, penalty_type):
        return cls.original_to_min_dict[cls.max_to_original_dict[penalty_type]]
