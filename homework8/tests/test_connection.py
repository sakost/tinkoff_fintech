from unittest import mock

import pytest

from app import connection
from app.schemas import MessageModel, UserModel
from app.utils import ReservedIdsEnum


class TestConnectionManager:
    @pytest.mark.asyncio
    async def test_connect(self, ws: mock.AsyncMock):
        mgr = connection.ConnectionManager()

        await mgr.connect(1, ws)
        assert mgr.active_connections[1] == ws
        assert ws.accept.await_count == 1

    @pytest.mark.asyncio
    async def test_disconnect(self, ws: mock.AsyncMock):
        mgr = connection.ConnectionManager()

        mgr.active_connections[0] = ws
        await mgr.disconnect(0)
        assert mgr.active_connections == {}

    @pytest.mark.asyncio
    async def test_send_personal_message(
        self, ws: mock.AsyncMock, message: MessageModel
    ):
        mgr = connection.ConnectionManager()
        mgr.active_connections[message.sender.client_id] = ws
        mgr.active_connections[message.destination.client_id] = ws

        await mgr.send_personal_message(message)

        assert ws.send_json.call_count == 1

    @pytest.mark.asyncio
    async def test_service_message(self, ws: mock.AsyncMock, message: MessageModel):
        mgr = connection.ConnectionManager()
        mgr.active_connections[message.sender.client_id] = ws
        mgr.active_connections[message.destination.client_id] = ws

        await mgr.service_message(message)
        assert ws.send_json.call_count == 1

        message.destination.client_id = ReservedIdsEnum.BROADCAST_ID.value
        await mgr.service_message(message)

        assert ws.send_json.call_count == 3

    @pytest.mark.asyncio
    async def test_broadcast(self, ws: mock.AsyncMock, message: MessageModel):
        mgr = connection.ConnectionManager()
        mgr.active_connections[message.sender.client_id] = ws
        mgr.active_connections[message.destination.client_id] = ws

        await mgr.broadcast(message)
        assert ws.send_json.call_count == 2

    @pytest.mark.asyncio
    async def test_get_next_message(self, ws: mock.AsyncMock, message: MessageModel):
        mgr = connection.ConnectionManager()
        mgr.active_connections[message.sender.client_id] = ws
        mgr.active_connections[message.destination.client_id] = ws

        ws.receive_json.return_value = message.dict()

        result = await mgr.get_next_message(message.sender.client_id)
        assert result == message

    def test_is_client_exists(self, ws: mock.AsyncMock):
        mgr = connection.ConnectionManager()
        user = UserModel(client_id=1)
        mgr.active_connections[1] = ws

        assert mgr.is_client_exists(user)
        assert mgr.is_client_exists(1)
