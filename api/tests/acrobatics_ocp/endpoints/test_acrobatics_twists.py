import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics import (
    router,
)
from bioptim_gui_api.acrobatics_ocp.misc.acrobatics_data import AcrobaticsOCPData
from bioptim_gui_api.acrobatics_ocp.misc.phase_updating import update_phase_info

test_app = FastAPI()
test_app.include_router(router)
client = TestClient(test_app)


@pytest.fixture(autouse=True)
def run_for_all():
    # before test: create file

    datafile = AcrobaticsOCPData.datafile

    with open(datafile, "w") as f:
        json.dump(AcrobaticsOCPData.base_data, f)

    update_phase_info()

    yield

    # after test : delete file
    import os

    os.remove(datafile)


def test_put_nb_half_twists():
    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_half_twists"] == [0]

    response = client.put(
        "/acrobatics/nb_half_twists/0",
        json={"nb_half_twists": 1},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_half_twists"] == [1]


def test_put_nb_half_twists_wrong():
    response = client.put(
        "/acrobatics/nb_half_twists/0",
        json={"nb_half_twists": -1},
    )
    assert response.status_code == 400, response

    response = client.put(
        "/acrobatics/nb_half_twists/0",
        json={"nb_half_twists": 0},
    )
    assert response.status_code == 200, response


def test_put_nb_half_twists_wrong_type():
    response = client.put(
        "/acrobatics/nb_half_twists/0",
        json={"nb_half_twists": "wrong"},
    )
    assert response.status_code == 422, response
