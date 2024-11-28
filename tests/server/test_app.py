import pytest
import httpx
from starlette.testclient import TestClient
from server.starlette_app import server, app


@pytest.fixture
def client():
    return TestClient(server)


def test_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_watcher_valid(client):
    response = client.post("/add-watcher", data={"function_name": "test_function"})
    assert response.status_code == 200


def test_pending_watchers(client):
    response = client.get("/pending-function-names")
    assert response.status_code == 200
    assert "function_names" in response.json()


def test_add_process_valid_json(client):
    data = {
        "event_name": "add-process",
        "system_info": {"process": {"instance_id": "test-123"}},
    }
    response = client.post("/events", json=data)
    assert response.status_code == 200


def test_add_process_invalid_json(client):
    response = client.post("/events", data="invalid json")
    assert response.status_code == 400


def test_add_process_missing_system_info(client):
    data = {"event_name": "add-process"}
    response = client.post("/events", json=data)
    assert response.status_code == 400


def test_confirm_watcher_valid(client):
    data = {"event_name": "confirm-watcher", "function_name": "test_function"}
    response = client.post("/events", json=data)
    assert response.status_code == 200


def test_confirm_watcher_invalid_json(client):
    response = client.post("/events", data="invalid json")
    assert response.status_code == 400


def test_confirm_watcher_missing_function_name(client):
    data = {"event_name": "confirm-watcher"}
    response = client.post("/events", json=data)
    assert response.status_code == 400


def test_function_call_valid(client):
    data = {
        "event_name": "log-function-call",
        "function_name": "test_function",
        "execution_time_ms": 100,
    }
    response = client.post("/events", json=data)
    assert response.status_code == 200


def test_function_call_invalid_json(client):
    response = client.post("/events", data="invalid json")
    assert response.status_code == 400


def test_function_call_missing_function_name(client):
    data = {"event_name": "log-function-call"}
    response = client.post("/events", json=data)
    assert response.status_code == 400


def test_invalid_event_name(client):
    data = {"event_name": "invalid-event"}
    response = client.post("/events", json=data)
    assert response.status_code == 400
    assert response.json()["error"] == "Invalid event name"


def test_missing_event_name(client):
    data = {}
    response = client.post("/events", json=data)
    assert response.status_code == 400
    assert response.json()["error"] == "Missing event_name"


def test_response_stream(client):
    # Add a watcher first
    function_name = "test_watcher"
    app.add_watcher(function_name)

    # Log a function call to trigger the stream
    test_data = {"args": [1, 2], "kwargs": {"test": "value"}}
    app.log_function_call(function_name, test_data)

    # Now that data is in queue, start reading the stream
    response = client.get(f"/watcher-stream?function_name={function_name}&max_events=1")
    chunks = []
    for chunk in response.iter_text(chunk_size=1024):
        chunks.append(chunk)

    assert len(chunks) == 1
    assert "event: SomeEventName" in chunks[0]
    assert "test_watcher(1, 2, test=value)" in chunks[0]


@pytest.mark.asyncio
async def test_watcher_stream_async():
    async with httpx.AsyncClient(app=server, base_url="http://test") as client:
        function_name = "test_watcher"
        app.add_watcher(function_name)
        test_data = {"args": [1, 2], "kwargs": {"test": "value"}}
        app.log_function_call(function_name, test_data)

        url = f"/watcher-stream?function_name={function_name}&max_events=1"
        response = await client.get(url)

        chunks = []
        async for chunk in response.aiter_text():
            chunks.append(chunk)

        assert len(chunks) == 1
        assert "event: SomeEventName" in chunks[0]
        assert "test_watcher(1, 2, test=value)" in chunks[0]
