import datetime
import uuid

from src.settings import HOURLY_RATE
from src.utils import current_datetime
from src.schemas import SECONDS_IN_HOUR


NETWORK_LATENCY = datetime.timedelta(seconds=2)


def compare_floats(a, b, tol=1e-06):
    return abs(a - b) < tol


def compare_datetimes(a, b, tol=NETWORK_LATENCY):
    return abs((a - b).total_seconds()) < tol.total_seconds()


def test_read_create_task_flow(client):
    # check no tasks
    response = client.get("/tasks")
    assert response.status_code == 200, response.content
    assert response.json() == [], response.content

    # create task
    response = client.post("/tasks", json={"name": "task1"})
    assert response.status_code == 201, response.content
    assert response.json()["name"] == "task1", response.content
    task_id = response.json()["id"]

    # check exist 1 task
    response = client.get("/tasks")
    assert response.status_code == 200, response.content
    assert len(response.json()) == 1, response.content

    # check correct reading task by id
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200, response.content
    assert response.json()["name"] == "task1", response.content

    # check fail reading task with not existing id
    response = client.get(f"/tasks/{uuid.uuid4()}")
    assert response.status_code == 404, response.content


def test_change_task_status_flow(client):
    # create task
    response = client.post("/tasks", json={"name": "task1"})
    assert response.status_code == 201, response.content
    assert response.json()["name"] == "task1", response.content
    task_id = response.json()["id"]

    # check status
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200, response.content
    assert response.json()["status"] == "TODO", response.content

    # check not correct status
    response = client.patch(f"/tasks/{task_id}", json={"status": "DONE"})
    assert response.status_code == 403, response.content

    # check correct updating status
    response = client.patch(f"/tasks/{task_id}", json={"status": "IN_PROGRESS"})
    assert response.status_code == 200, response.content
    assert response.json()["status"] == "IN_PROGRESS", response.content
    start_time = datetime.datetime.fromisoformat(response.json()["start_time"])
    assert compare_datetimes(current_datetime(), start_time), response.content

    # check not correct status
    response = client.patch(f"/tasks/{task_id}", json={"status": "TODO"})
    assert response.status_code == 403, response.content

    # check saving status
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200, response.content
    assert response.json()["status"] == "IN_PROGRESS", response.content

    # check correct updating status
    response = client.patch(f"/tasks/{task_id}", json={"status": "DONE"})
    assert response.status_code == 200, response.content
    assert response.json()["status"] == "DONE", response.content
    start_time = datetime.datetime.fromisoformat(response.json()["start_time"])
    end_time = datetime.datetime.fromisoformat(response.json()["end_time"])
    expected_price = (
        HOURLY_RATE * (end_time - start_time).total_seconds() / SECONDS_IN_HOUR
    )
    expected_time_in_work = (end_time - start_time).total_seconds()
    assert compare_datetimes(current_datetime(), end_time), response.content
    assert compare_floats(response.json()["price"], expected_price), response.content
    assert compare_floats(
        response.json()["time_in_work"], expected_time_in_work
    ), response.content

    # check saving status
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200, response.content
    assert response.json()["status"] == "DONE", response.content
    start_time = datetime.datetime.fromisoformat(response.json()["start_time"])
    end_time = datetime.datetime.fromisoformat(response.json()["end_time"])
    expected_price = (
        HOURLY_RATE * (end_time - start_time).total_seconds() / SECONDS_IN_HOUR
    )
    expected_time_in_work = (end_time - start_time).total_seconds()
    assert compare_floats(response.json()["price"], expected_price), response.content
    assert compare_floats(
        response.json()["time_in_work"], expected_time_in_work
    ), response.content
