from enum import Enum

from pydantic import UUID4, BaseModel


class TaskStatusEnum(Enum):
    WAITING = 'WAITING'
    IN_PROGRESS = 'IN_PROGRESS'
    DONE = 'DONE'
    FAILED = 'FAILED'

    @classmethod
    def from_rq(cls, data: str) -> 'TaskStatusEnum':
        mapping = {
            'failed': cls.FAILED,
            'stopped': cls.FAILED,
            'finished': cls.DONE,
            'started': cls.IN_PROGRESS,
            'queued': cls.WAITING,
            'deferred': cls.WAITING,
        }
        return mapping[data.lower()]


class ImageSize(Enum):
    IMAGE32 = '32'
    IMAGE64 = '64'
    IMAGE_ORIGINAL = 'original'


class ImageResult(BaseModel):
    IMAGE32: bytes
    IMAGE64: bytes
    IMAGE_ORIGINAL: bytes


class TaskStatusGet(BaseModel):
    id: UUID4
    status: TaskStatusEnum
