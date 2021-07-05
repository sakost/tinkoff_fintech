from .schemas import ImageResult
from .utils import decode_image, encode_image


def process_image(image_data: bytes) -> ImageResult:
    image = decode_image(image_data)
    image64 = image.resize((64, 64))
    image32 = image.resize((32, 32))
    return ImageResult(
        IMAGE32=encode_image(image32),
        IMAGE64=encode_image(image64),
        IMAGE_ORIGINAL=encode_image(image),
    )
