import inspect
import re

import bioptim
from bioptim import ObjectiveFcn
from fastapi import HTTPException


def format_arg_type(arg_type: str) -> str:
    """
    Format the type of the argument

    Parameters
    ----------
    arg_type: str
        The type of the argument (e.g. "<class 'list'>", "float")

    Returns
    -------
    The formatted type (e.g. "list", "float")
    """
    pattern = r"<(class|enum) '(.*)'>"
    arg_type = str(arg_type)
    match = re.search(pattern, arg_type)
    return match and match.group(2) or arg_type


def get_args(penalty_fcn) -> list:
    """
    Get the arguments of the penalty function

    Parameters
    ----------
    penalty_fcn: ObjectiveFcn or ConstraintFcn
        The penalty function

    Returns
    -------
    The list of arguments (e.g. [{"name": "state_idx", "value": None, "type": "list"}])
    with "value" being the defaults value
    """
    penalty_fcn = penalty_fcn.value[0]
    # arguments
    arg_specs = inspect.getfullargspec(penalty_fcn)
    defaults = arg_specs.defaults
    arguments = arg_specs.annotations

    formatted_arguments = [{"name": k, "value": None, "type": format_arg_type(v)} for k, v in arguments.items()]

    if defaults:
        l_defaults = len(defaults)
        for i in range(l_defaults):
            formatted_arguments[-l_defaults + i]["value"] = defaults[i]

    formatted_arguments = [arg for arg in formatted_arguments if arg["name"] not in ("_", "penalty", "controller")]

    return formatted_arguments


def obj_arguments(objective_type: str, penalty_type: str) -> list:
    """
    Get the arguments of the objective function

    Parameters
    ----------
    objective_type: str
        The type of objective ("mayer" or "lagrange")
    penalty_type: str
        The type of penalty (ObjectiveFcn.Mayer or ObjectiveFcn.Lagrange, e.g. "MINIMIZE_STATE")

    Returns
    -------
    The list of arguments (e.g. [{"name": "state_idx", "value": None, "type": "list"}])
    """

    if penalty_type == "CUSTOM":
        return [{"name": "function", "value": None, "type": "function"}]

    try:
        if objective_type == "mayer":
            penalty_fcn = getattr(ObjectiveFcn.Mayer, penalty_type)
        elif objective_type == "lagrange":
            penalty_fcn = getattr(ObjectiveFcn.Lagrange, penalty_type)
        arguments = get_args(penalty_fcn)
    except AttributeError as e:
        raise AttributeError(f"{penalty_type} not found from {e}") from e
    except Exception as e:
        raise HTTPException(500, f"{objective_type} not found from {e}") from e

    return arguments


def constraint_arguments(penalty_type: str) -> list:
    """
    Get the arguments of the constraint function

    Parameters
    ----------
    penalty_type: str
        The type of penalty (ConstraintFcn, e.g. "SUPERIMPOSE_MARKERS")

    Returns
    -------
    The list of arguments (e.g. [{"name": "state_idx", "value": None, "type": "list"}])
    """
    penalty_type = penalty_type.upper().replace(" ", "_")
    try:
        penalty_fcn = getattr(bioptim.ConstraintFcn, penalty_type)
    except AttributeError as e:
        raise HTTPException(404, f"{penalty_type} not found from {e}") from e

    arguments = get_args(penalty_fcn)
    return arguments


def create_objective(**kwargs) -> dict:
    """
    Create an objective without having to specify all the arguments if they are the default ones.

    Parameters
    ----------
    kwargs: dict
        The information on the objective (e.g. {"objective_type": "lagrange", "penalty_type": "MINIMIZE_STATE", ...})

    Returns
    -------
    dict
        The objective
    """
    return {
        "objective_type": kwargs.get("objective_type", "lagrange"),
        "penalty_type": kwargs.get("penalty_type", "MINIMIZE_STATE"),
        "nodes": kwargs.get("nodes", "all_shooting"),
        "quadratic": kwargs.get("quadratic", True),
        "expand": kwargs.get("expand", True),
        "target": kwargs.get("target", None),
        "derivative": kwargs.get("derivative", False),
        "integration_rule": kwargs.get("integration_rule", "rectangle_left"),
        "multi_thread": kwargs.get("multi_thread", False),
        "weight": kwargs.get("weight", 1.0),
        "arguments": kwargs.get("arguments", []),
    }


def create_constraint(**kwargs) -> dict:
    """
    Create a constraint without having to specify all the arguments if they are the default ones.

    Parameters
    ----------
    kwargs: dict
        The information on the constraint (e.g. {"penalty_type": "SUPERIMPOSE_MARKERS", ...})

    Returns
    -------
    dict
        The constraint
    """
    return {
        "penalty_type": kwargs.get("penalty_type", "TIME_CONSTRAINT"),
        "nodes": kwargs.get("nodes", "end"),
        "quadratic": kwargs.get("quadratic", True),
        "expand": kwargs.get("expand", True),
        "target": kwargs.get("target", None),
        "derivative": kwargs.get("derivative", False),
        "integration_rule": kwargs.get("integration_rule", "rectangle_left"),
        "multi_thread": kwargs.get("multi_thread", False),
        "arguments": kwargs.get("arguments", []),
    }


def penalty_str_to_non_collision_penalty(stringified: str) -> str:
    """
    Convert a stringified penalty to a non-collision penalty

    Parameters
    ----------
    stringified: str
        The stringified penalty

    Returns
    -------
    str
        The non-collision penalty
    """
    ret = """add_non_crossing_penalty(
        objective_functions,
        constraints,
        warming_up,
"""
    lines = stringified.split("\n")
    # remove lines that starts wtih custom_noncrossing_const
    updated_lines = [line for line in lines if not line.startswith("custom_noncrossing_")]

    ret += "\n".join(updated_lines) + "    )"
    return ret
