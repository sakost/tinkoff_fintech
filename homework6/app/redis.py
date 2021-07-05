from redis import Redis, from_url  # pylint: disable=unused-import
from rq import Queue

from .config import settings
from .utils import singleton_cache


@singleton_cache
def redis_client() -> 'Redis[Queue]':
    return from_url(settings().REDIS_URL)


@singleton_cache
def image_processing_queue() -> Queue:
    return Queue(name='image_processing', connection=redis_client())


listen = ['image_processing']
