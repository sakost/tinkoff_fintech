from fastapi.testclient import TestClient


def test_app(client: TestClient):
    client.get('/')
