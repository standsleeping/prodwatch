import pytest
from starlette.testclient import TestClient
from web.starlette_app import server

@pytest.fixture
def client():
    return TestClient(server)


def test_homepage(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Home" in response.text
    assert '<form hx-post="/watch-function"' in response.text


def test_submit_function_watch(client):
    response = client.post("/watch-function", data={"function_names": "test_function"})
    assert response.status_code == 200
