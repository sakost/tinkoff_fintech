from unittest import mock

import pytest
from fastapi import WebSocket
from fastapi.testclient import TestClient

import app.app
from app.schemas import MessageModel, UserModel


@pytest.fixture()
def ws() -> WebSocket:
    return mock.AsyncMock(spec=WebSocket)


@pytest.fixture()
def message():
    return MessageModel(
        sender=UserModel(
            client_id=2,
        ),
        destination=UserModel(
            client_id=3,
        ),
        text='some text',
    )


@pytest.fixture()
def client():
    return TestClient(app.app.app)
