from unittest import mock

from fastapi.testclient import TestClient


@mock.patch('app.endpoints.redis_mgr', new_callable=mock.AsyncMock)
def test_connect(patched, client: TestClient):
    patched.get_last_messages.return_value = [{'text': 'some text'}]
    assert client.get('/last_messages').json()['messages'] == [{'text': 'some text'}]
