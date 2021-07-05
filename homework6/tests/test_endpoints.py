from http import HTTPStatus
from io import BytesIO
from unittest import mock

import pytest
from fastapi.testclient import TestClient
from PIL import Image
from rq.job import Job

from app import endpoints, process
from app.utils import encode_image


def test_add_redis_task(image_file: BytesIO, image_base64: str):
    with mock.patch('rq.Queue') as queue:
        endpoints.add_redis_task(image_file, queue)
        queue.enqueue.assert_called_once_with(
            process.process_image, image_base64.encode(), result_ttl='1d'
        )


@mock.patch('app.endpoints.add_redis_task')
def test_create_task(patch, client: TestClient, image_file: BytesIO):
    patch.return_value = patch
    patch.get_status.return_value = 'started'
    patch.id = 'bcf39911-0f2b-4f53-961f-f522eabc7410'

    response = client.post('/tasks', files={'file': image_file})

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 'bcf39911-0f2b-4f53-961f-f522eabc7410',
        'status': 'IN_PROGRESS',
    }


class TestGetTask:
    def test_success(self, fake_task: Job, client: TestClient):
        response = client.get(f'/tasks/{fake_task.id}', json={})
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {'id': fake_task.id, 'status': 'DONE'}

    def test_fail(self, client: TestClient):
        response = client.get('/tasks/bcf39911-0f2b-4f53-961f-f522eabc7410')
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestImage:
    @pytest.mark.parametrize(
        'image_size',
        [
            'original',
            '32',
            '64',
        ],
    )
    def test_success(
        self, fake_task: Job, client: TestClient, image_base64: str, image_size: str
    ):
        response = client.get(
            f'/tasks/{fake_task.id}/image', params={'size': image_size}
        )

        assert response.status_code == HTTPStatus.OK
        image = Image.open(BytesIO(response.content))
        assert encode_image(image) == image_base64.encode()

    def test_fail(self, client: TestClient) -> None:
        response = client.get(
            '/tasks/bcf39911-0f2b-4f53-961f-f522eabc7410/image', params={'size': '32'}
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
