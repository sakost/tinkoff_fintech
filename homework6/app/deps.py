from redis import Redis  # pylint: disable=unused-import
from rq import Queue

from .redis import image_processing_queue, redis_client


def get_redis() -> 'Redis[Queue]':
    return redis_client()


def get_image_processing_queue() -> Queue:
    return image_processing_queue()
