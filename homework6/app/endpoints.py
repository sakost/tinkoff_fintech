from http import HTTPStatus
from io import BytesIO
from typing import IO, Any, Optional

from fastapi import APIRouter, Depends, File, UploadFile
from PIL import Image
from pydantic import UUID4
from rq import Queue
from rq.job import Job
from starlette.responses import StreamingResponse

from .deps import get_image_processing_queue
from .exceptions import InvalidTaskId, InvalidTaskStatus
from .process import process_image
from .schemas import ImageSize, TaskStatusEnum, TaskStatusGet
from .utils import decode_image, encode_image

router = APIRouter()


def add_redis_task(
    image_data: IO[bytes],
    image_processing_queue: Queue,
) -> Job:
    image: Image.Image = Image.open(image_data)
    job: Job = image_processing_queue.enqueue(
        process_image, encode_image(image), result_ttl='1d'
    )
    return job


@router.post('/tasks', status_code=HTTPStatus.CREATED, response_model=TaskStatusGet)
def create_task(
    file: UploadFile = File(...),
    image_processing_queue: Queue = Depends(get_image_processing_queue),
) -> Any:
    job = add_redis_task(file.file, image_processing_queue)
    return {'id': job.id, 'status': TaskStatusEnum.from_rq(job.get_status())}


@router.get('/tasks/{task_id}', response_model=TaskStatusGet)
def get_task(
    task_id: UUID4, image_processing_queue: Queue = Depends(get_image_processing_queue)
) -> Any:
    job: Optional[Job] = image_processing_queue.fetch_job(str(task_id))
    if job is None:
        raise InvalidTaskId
    status = job.get_status()
    return {'id': job.id, 'status': TaskStatusEnum.from_rq(status)}


@router.get('/tasks/{task_id}/image')
def get_image(
    task_id: UUID4,
    size: ImageSize,
    image_processing_queue: Queue = Depends(get_image_processing_queue),
) -> StreamingResponse:
    job: Optional[Job] = image_processing_queue.fetch_job(str(task_id))
    if job is None:
        raise InvalidTaskId
    if TaskStatusEnum.from_rq(job.get_status()) != TaskStatusEnum.DONE:
        raise InvalidTaskStatus

    if size == ImageSize.IMAGE_ORIGINAL:
        image_data = job.result.IMAGE_ORIGINAL
    elif size == ImageSize.IMAGE64:
        image_data = job.result.IMAGE64
    else:
        image_data = job.result.IMAGE32

    image = decode_image(image_data)
    buffer = BytesIO()
    image.save(buffer, 'png')
    buffer.seek(0)
    return StreamingResponse(buffer, media_type='image/png')
