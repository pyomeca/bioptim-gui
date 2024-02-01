import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bioptim_gui_api.generic_ocp.endpoints.generic_ocp import router
from bioptim_gui_api.generic_ocp.misc.generic_ocp_data import GenericOCPData

test_app = FastAPI()
test_app.include_router(router)
client = TestClient(test_app)


@pytest.fixture(autouse=True)
def run_for_all():
    # before test: create file
    datafile = GenericOCPData.datafile

    with open(datafile, "w") as f:
        json.dump(GenericOCPData.base_data, f)

    yield

    # after test : delete file
    import os

    os.remove(datafile)


def test_generate_code_work():
    response = client.get("/generic_ocp/generate_code")
    assert response.status_code == 200, response
    data = response.json()
    assert type(data) is str
    assert len(data) != 0
