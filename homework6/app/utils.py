from base64 import b64decode, b64encode
from io import BytesIO
from typing import Any, Callable, Optional, TypeVar

from PIL import Image

T = TypeVar('T')


def singleton_cache(func: Callable[..., T]) -> Callable[..., T]:
    instance: Optional[T] = None

    def wrapper(*args: Any, **kwargs: Any) -> T:
        nonlocal instance
        if instance is None:
            instance = func(*args, **kwargs)
        return instance

    return wrapper


def image_to_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, 'png')
    return buffer.getvalue()


def bytes_to_image(data: bytes) -> Image.Image:
    buffer = BytesIO(data)
    return Image.open(buffer)


def encode_image(image: Image.Image) -> bytes:
    return b64encode(image_to_bytes(image))


def decode_image(data: bytes) -> Image.Image:
    return bytes_to_image(b64decode(data))
