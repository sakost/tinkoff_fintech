import asyncio
from dataclasses import dataclass
from typing import Optional

import aioredis
import async_timeout
from fastapi import APIRouter

from .schemas import MessageModel
from .settings import settings
from .utils import ReservedIdsEnum

router = APIRouter()


def init_redis() -> aioredis.Redis:
    return aioredis.Redis.from_url(url=settings.REDIS_URL, decode_responses=True)


redis = init_redis()


@dataclass(frozen=True)
class RedisManagerElement:
    pubsub: aioredis.client.PubSub
    channel_name: str


class RedisManager:
    REDIS_MESSAGES_LIST_NAME = 'messages'
    REDIS_MAX_MESSAGES_STORE = 50

    def __init__(self, redis_interface: aioredis.Redis):
        self.active_users: dict[int, RedisManagerElement] = {}
        self._redis = redis_interface

    async def connect(self, client_id: int) -> None:
        pubsub = self._redis.pubsub()
        cur_client = self.active_users[client_id] = RedisManagerElement(
            pubsub, self.get_channel_name(client_id)
        )
        await pubsub.subscribe(cur_client.channel_name)

    async def disconnect(self, client_id: int) -> None:
        cur_client = self.active_users[client_id]
        await cur_client.pubsub.unsubscribe(cur_client.channel_name)

        await cur_client.pubsub.reset()
        await cur_client.pubsub.close()

        del self.active_users[client_id]

    async def get_last_messages(self, count: int = 50) -> list[MessageModel]:
        return list(
            map(
                MessageModel.parse_raw,
                await self._redis.lrange(self.REDIS_MESSAGES_LIST_NAME, 0, count - 1),
            )
        )

    async def send_personal_message(
        self, message: MessageModel, save_to_redis: bool = True
    ) -> None:
        if message.is_broadcast():
            await self.broadcast(message)
            return
        client_id = message.destination.client_id
        if save_to_redis:
            await self._save_message(message)
        await self._redis.publish(self.get_channel_name(client_id), message.json())

    async def _save_message(
        self, message: MessageModel, count: Optional[int] = None
    ) -> None:
        if count is None:
            count = self.REDIS_MAX_MESSAGES_STORE
        async with self._redis.pipeline(transaction=True) as pipe:
            # noinspection PyAsyncCall
            pipe.rpush(self.REDIS_MESSAGES_LIST_NAME, message.json())
            # noinspection PyAsyncCall
            pipe.ltrim(
                self.REDIS_MESSAGES_LIST_NAME,
                -count,  # pylint: disable=invalid-unary-operand-type
                -1,
            )
            await pipe.execute()

    async def broadcast(self, message: MessageModel) -> None:
        for client_id in self.active_users:
            message.destination.client_id = client_id
            await self.send_personal_message(message, save_to_redis=False)

        message.destination.client_id = ReservedIdsEnum.BROADCAST_ID.value
        await self._save_message(message)

    @staticmethod
    def get_channel_name(client_id: int) -> str:
        return f'channel:{client_id}'

    async def get_next_message(self, client_id: int) -> MessageModel:
        cur_client = self.active_users[client_id]
        while True:
            try:
                async with async_timeout.timeout(1):
                    message = await cur_client.pubsub.get_message(
                        ignore_subscribe_messages=True
                    )
                    if message is not None:
                        return MessageModel.parse_raw(message['data'])
                await asyncio.sleep(0.01)
            except asyncio.TimeoutError:
                pass


manager = RedisManager(redis)
