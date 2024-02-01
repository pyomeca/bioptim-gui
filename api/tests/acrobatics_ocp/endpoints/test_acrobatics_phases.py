import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from bioptim_gui_api.acrobatics_ocp.endpoints.acrobatics import router
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
        base_data = AcrobaticsOCPData.base_data
        json.dump(base_data, f)

    update_phase_info()

    yield

    # after test : delete file
    import os

    os.remove(datafile)


def test_get_phases_info():
    response = client.get("/acrobatics/phases_info/")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 2
    assert data[0]["duration"] == 0.5
    assert len(data[0]["objectives"]) == 5
    assert len(data[0]["constraints"]) == 0
    assert len(data[1]["objectives"]) == 4
    assert len(data[1]["constraints"]) == 0

    client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    response = client.get("/acrobatics/phases_info/")
    assert response.status_code == 200, response
    data = response.json()
    assert len(data) == 3
    assert data[0]["duration"] == 0.33
    assert len(data[0]["objectives"]) == 5
    assert len(data[0]["constraints"]) == 0
    assert len(data[1]["objectives"]) == 5
    assert len(data[1]["constraints"]) == 0
    assert len(data[2]["objectives"]) == 4
    assert len(data[2]["constraints"]) == 0


def test_get_somersault_with_index():
    response = client.get("/acrobatics/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 0.5
    assert len(data["objectives"]) == 5
    assert len(data["constraints"]) == 0


def test_get_somersault_with_index_wrong():
    response = client.get("/acrobatics/phases_info/2")
    assert response.status_code == 404, response


def test_put_shooting_points():
    response = client.get("/acrobatics/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_shooting_points"] == 40

    response = client.put(
        "/acrobatics/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": 10},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["nb_shooting_points"] == 10


def test_put_shooting_points_wrong():
    response = client.put(
        "/acrobatics/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": -10},
    )
    assert response.status_code == 400, response

    response = client.put(
        "/acrobatics/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": 0},
    )
    assert response.status_code == 400, response


def test_put_shooting_points_wrong_type():
    response = client.put(
        "/acrobatics/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": "wrong"},
    )
    assert response.status_code == 422, response


def test_put_shooting_points_unchanged_other_somersaults():
    """
    add a somersault, change its shooting points, check that the other somersaults are unchanged
    """
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    assert response.status_code == 200, response

    response = client.put(
        "/acrobatics/phases_info/0/nb_shooting_points",
        json={"nb_shooting_points": 10},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/phases_info")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["nb_shooting_points"] == 10
    assert data[1]["nb_shooting_points"] == 40


def test_put_somersault_duration():
    response = client.get("/acrobatics/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 0.5

    response = client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": 0.6},
    )
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 0.6
    assert data["new_final_time"] == 1.1

    response = client.get("/acrobatics/phases_info/0")
    assert response.status_code == 200, response
    data = response.json()
    assert data["duration"] == 0.6


def test_put_somersault_duration_wrong():
    response = client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": -0.5},
    )
    assert response.status_code == 400, response

    response = client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": 0},
    )
    assert response.status_code == 400, response


def test_put_somersault_duration_wrong_type():
    response = client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": "wrong"},
    )
    assert response.status_code == 422, response


def test_put_somersault_duration_unchanged_other_somersaults():
    """
    add a somersault, change its duration, check that the other somersaults are unchanged
    """
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 2})
    assert response.status_code == 200, response

    response = client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": 0.2},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/phases_info")
    assert response.status_code == 200, response
    data = response.json()
    assert data[0]["duration"] == 0.2
    assert data[1]["duration"] == 0.33


def test_put_somersault_duration_changes_final_time_simple_more():
    response = client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": 1.2},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["final_time"] == 1.7


def test_put_somersault_duration_changes_final_time_simple_less():
    response = client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": 0.2},
    )
    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["final_time"] == 0.7


def test_put_somersault_duration_changes_final_time_simple_more_multiple():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 4})
    assert response.status_code == 200, response

    client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": 1.2},
    )

    response = client.put(
        "/acrobatics/phases_info/1/duration",
        json={"duration": 0.6},
    )
    # durations : 1.2, 0.6, 0.2, 0.2, 0.2 final_time = 2.4

    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["final_time"] == 2.4


def test_put_somersault_duration_changes_final_time_simple_less_multiple():
    response = client.put("/acrobatics/nb_somersaults/", json={"nb_somersaults": 4})
    assert response.status_code == 200, response

    client.put(
        "/acrobatics/phases_info/0/duration",
        json={"duration": 0.1},
    )

    response = client.put(
        "/acrobatics/phases_info/1/duration",
        json={"duration": 0.1},
    )
    # durations : 0.1, 0.1, 0.2, 0.2, 0.2 final_time = 0.8

    assert response.status_code == 200, response

    response = client.get("/acrobatics/")
    assert response.status_code == 200, response
    data = response.json()
    assert data["final_time"] == 0.8
