import json
from typing import Optional, Union

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from .schemas import MessageModel, UserModel
from .utils import ReservedIdsEnum


class ConnectionManager:
    __slots__ = ('active_connections',)

    INVALID_MESSAGE = MessageModel(
        sender=UserModel(client_id=ReservedIdsEnum.SERVICE_MESSAGES_ID.value),
        destination=UserModel(client_id=ReservedIdsEnum.SERVICE_MESSAGES_ID.value),
        text='Invalid message format',
    )

    def __init__(self) -> None:
        self.active_connections: dict[int, WebSocket] = {}  # pragma: no cover

    async def connect(self, client_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections[client_id] = websocket

    async def disconnect(self, client_id: int) -> None:
        del self.active_connections[client_id]

    async def send_personal_message(
        self, message: MessageModel, destination_websocket: Optional[WebSocket] = None
    ) -> None:
        if message.is_broadcast():
            return await self.broadcast(message)

        if not destination_websocket:
            destination_websocket = self.active_connections[
                message.destination.client_id
            ]

        await destination_websocket.send_json(message.json())

    async def service_message(
        self, message: MessageModel, destination_websocket: Optional[WebSocket] = None
    ) -> None:
        if message.destination.client_id == ReservedIdsEnum.BROADCAST_ID.value:
            return await self.broadcast(message)
        return await self.send_personal_message(message, destination_websocket)

    async def broadcast(self, message: MessageModel) -> None:
        for connection in self.active_connections.values():
            await connection.send_json(message.json())

    async def get_next_message(self, client_id: int) -> Optional[MessageModel]:
        websocket = self.active_connections[client_id]
        try:
            try:
                json_message = await websocket.receive_json()
                return MessageModel.parse_obj(json_message)
            except ValidationError:
                await self.service_message(self.INVALID_MESSAGE, websocket)
        except json.JSONDecodeError:
            await self.service_message(self.INVALID_MESSAGE, websocket)
        except WebSocketDisconnect:
            pass
        return None

    def is_client_exists(self, client: Union[int, UserModel]) -> bool:
        if isinstance(client, UserModel):
            client = client.client_id
        return (
            client in self.active_connections
            or client == ReservedIdsEnum.BROADCAST_ID.value
        )


manager = ConnectionManager()
