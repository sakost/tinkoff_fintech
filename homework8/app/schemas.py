from typing import Any

from pydantic import BaseModel, Field

from .utils import ReservedIdsEnum


class UserModel(BaseModel):
    client_id: int = Field(ge=ReservedIdsEnum.BROADCAST_ID.value)


class MessageModel(BaseModel):
    sender: UserModel
    destination: UserModel
    text: str

    @classmethod
    def create_broadcast(cls, **kwargs: Any) -> 'MessageModel':
        kwargs['destination'] = UserModel(client_id=ReservedIdsEnum.BROADCAST_ID.value)
        return cls(**kwargs)

    @classmethod
    def create_service_message(cls, **kwargs: Any) -> 'MessageModel':
        kwargs['sender'] = UserModel(
            client_id=ReservedIdsEnum.SERVICE_MESSAGES_ID.value
        )
        return cls(**kwargs)

    def is_broadcast(self) -> bool:
        return self.destination.client_id == ReservedIdsEnum.BROADCAST_ID.value

    def is_service(self) -> bool:
        return self.sender.client_id == ReservedIdsEnum.SERVICE_MESSAGES_ID.value
