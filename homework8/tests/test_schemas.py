from app import schemas
from app.utils import ReservedIdsEnum


def test_create_broadcast():
    message = schemas.MessageModel.create_broadcast(
        sender=schemas.UserModel(client_id=3),
        destination=schemas.UserModel(client_id=4),
        text='some text',
    )
    assert message.destination.client_id == ReservedIdsEnum.BROADCAST_ID.value


def test_create_service_message():
    message = schemas.MessageModel.create_service_message(
        sender=schemas.UserModel(client_id=3),
        destination=schemas.UserModel(client_id=4),
        text='some text',
    )
    assert message.sender.client_id == ReservedIdsEnum.SERVICE_MESSAGES_ID.value


def test_is_broadcast():
    message = schemas.MessageModel.create_broadcast(
        sender=schemas.UserModel(client_id=3),
        destination=schemas.UserModel(client_id=ReservedIdsEnum.BROADCAST_ID.value),
        text='some text',
    )
    assert message.is_broadcast()


def test_is_service():
    message = schemas.MessageModel.create_service_message(
        sender=schemas.UserModel(client_id=3),
        destination=schemas.UserModel(client_id=ReservedIdsEnum.BROADCAST_ID.value),
        text='some text',
    )
    assert message.is_service()
