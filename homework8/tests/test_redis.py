from unittest import mock

import pytest
from aioredis import Redis
from aioredis.client import PubSub

from app import redis
from app.redis import RedisManagerElement
from app.schemas import MessageModel


@mock.patch('aioredis.Redis.from_url')
def test_init_redis(patched):
    redis.init_redis()
    assert patched.call_count == 1


class TestRedisManager:
    @pytest.mark.asyncio
    async def test_connect(self):
        redis_mock = mock.AsyncMock(spec=Redis)
        pubsub_mock = mock.AsyncMock(spec=PubSub)
        redis_mock.pubsub.return_value = pubsub_mock
        mgr = redis.RedisManager(redis_mock)
        await mgr.connect(1)
        assert mgr.active_users[1] == RedisManagerElement(pubsub_mock, 'channel:1')

    @pytest.mark.asyncio
    async def test_disconnect(self):
        async def coro():
            pass

        redis_mock = mock.AsyncMock(spec=Redis)
        pubsub_mock = mock.AsyncMock(spec=PubSub)

        redis_mock.pubsub.return_value = pubsub_mock
        pubsub_mock.unsubscribe.return_value = coro()
        pubsub_mock.close.return_value = coro()

        data = RedisManagerElement(pubsub_mock, 'channel:1')

        mgr = redis.RedisManager(redis_mock)
        mgr.active_users[1] = data

        await mgr.disconnect(1)

        assert len(mgr.active_users) == 0
        assert pubsub_mock.unsubscribe.called
        assert pubsub_mock.reset.called
        assert pubsub_mock.close.called

    @pytest.mark.asyncio
    async def test_get_last_messages(self, message: MessageModel):
        async def coro():
            return [message.json()]

        redis_mock = mock.AsyncMock(spec=Redis)
        pubsub_mock = mock.AsyncMock(spec=PubSub)

        redis_mock.pubsub.return_value = pubsub_mock
        redis_mock.lrange.return_value = coro()
        data = RedisManagerElement(pubsub_mock, 'channel:1')

        mgr = redis.RedisManager(redis_mock)
        mgr.active_users[1] = data

        result = await mgr.get_last_messages()
        assert result == [message]

    def test_get_channel_name(self):
        redis_mock = mock.AsyncMock(spec=Redis)
        mgr = redis.RedisManager(redis_mock)
        assert mgr.get_channel_name(1) == 'channel:1'
        assert mgr.get_channel_name(-1) == 'channel:-1'
        assert mgr.get_channel_name(0) == 'channel:0'
