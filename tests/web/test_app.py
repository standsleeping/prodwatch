import pytest
from starlette.testclient import TestClient
from web.starlette_app import server


@pytest.fixture
def client():
    return TestClient(server)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_watcher_valid(client):
    response = client.post("/add-watcher", data={"function_name": "test_function"})
    assert response.status_code == 200


def test_add_process_valid_json(client):
    data = {"system_info": {"process": {"instance_id": "test-123"}}}
    response = client.post("/add-process", json=data)
    assert response.status_code == 200


def test_add_process_invalid_json(client):
    response = client.post("/add-process", data="invalid json")
    assert response.status_code == 400


def test_add_process_missing_system_info(client):
    response = client.post("/add-process", json={})
    assert response.status_code == 400


def test_pending_watchers(client):
    response = client.get("/pending-function-names")
    assert response.status_code == 200
    assert "function_names" in response.json()


def test_confirm_watcher_valid(client):
    data = {"function_name": "test_function"}
    response = client.post("/confirm-watcher", json=data)
    assert response.status_code == 200


def test_confirm_watcher_invalid_json(client):
    response = client.post("/confirm-watcher", data="invalid json")
    assert response.status_code == 400


def test_confirm_watcher_missing_function_name(client):
    response = client.post("/confirm-watcher", json={})
    assert response.status_code == 400


def test_function_call_valid(client):
    data = {"function_name": "test_function"}
    response = client.post("/log-function-call", json=data)
    assert response.status_code == 200


def test_function_call_invalid_json(client):
    response = client.post("/log-function-call", data="invalid json")
    assert response.status_code == 400


def test_function_call_missing_function_name(client):
    response = client.post("/log-function-call", json={})
    assert response.status_code == 400
