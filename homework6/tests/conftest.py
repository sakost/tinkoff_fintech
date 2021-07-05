# pylint: disable=redefined-outer-name
from typing import Iterator

import pytest
from fakeredis import FakeRedis
from fastapi.testclient import TestClient
from PIL import Image
from redis import Redis  # pylint: disable=unused-import
from rq import Queue
from rq.job import Job

from app.app import app
from app.deps import get_image_processing_queue, get_redis
from app.schemas import ImageResult


@pytest.fixture(scope='session')
def fake_redis_client() -> 'Redis[Queue]':
    return FakeRedis()


@pytest.fixture(scope='session')
def fake_queue(fake_redis_client) -> Queue:
    return Queue(connection=fake_redis_client, is_async=False)


@pytest.fixture(scope='session')
def client(fake_queue, fake_redis_client) -> TestClient:
    app.dependency_overrides[get_redis] = lambda: fake_redis_client
    app.dependency_overrides[get_image_processing_queue] = lambda: fake_queue
    return TestClient(app)


@pytest.fixture(scope='session')
def image() -> Image.Image:
    return Image.open('tests/data/img.png')


@pytest.fixture(scope='session')
def image_file() -> Iterator[Image.Image]:
    with open('tests/data/img.png', 'rb') as file:
        yield file


@pytest.fixture(scope='session')
def image_base64() -> str:
    with open('tests/data/img.base64.txt', 'r') as file:
        return file.read()


@pytest.fixture(scope='session')
def image32_base64() -> str:
    with open('tests/data/img32.base64.txt', 'r') as file:
        return file.read()


@pytest.fixture(scope='session')
def image64_base64() -> str:
    with open('tests/data/img64.base64.txt', 'r') as file:
        return file.read()


def fake_process(image_base64: str) -> ImageResult:
    image_data = image_base64.encode()
    return ImageResult(
        IMAGE_ORIGINAL=image_data,
        IMAGE64=image_data,
        IMAGE32=image_data,
    )


@pytest.fixture()
def fake_task(fake_queue: Queue, image_base64: str) -> Job:
    return fake_queue.enqueue(fake_process, image_base64)
