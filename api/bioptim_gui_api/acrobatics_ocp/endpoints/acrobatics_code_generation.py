from fastapi import APIRouter, HTTPException

from bioptim_gui_api.acrobatics_ocp.code_generation.acrobatics_generation_utils import generated_code, converted_model
from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics_responses import CodeGenerationResponse
from bioptim_gui_api.acrobatics_ocp.misc.acrobatics_data import AcrobaticsOCPData

router = APIRouter()


@router.post("/generate_code", response_model=CodeGenerationResponse)
def get_acrobatics_generated_code():
    data = AcrobaticsOCPData.read_data()

    model_path = data["model_path"]

    if not model_path:
        raise HTTPException(status_code=400, detail="No model path provided")

    new_models = converted_model(data)

    generated = generated_code(
        data,
        new_models[0].new_model_path,
        new_models[1].new_model_path if len(new_models) > 1 else None,
    )

    return CodeGenerationResponse(
        generated_code=generated,
        new_models=new_models,
    )
