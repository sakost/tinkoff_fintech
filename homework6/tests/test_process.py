from app import process


def test_process(image64_base64: str, image32_base64: str, image_base64: str) -> None:
    result = process.process_image(image_base64.encode())
    assert result.IMAGE64 == image64_base64.encode()
    assert result.IMAGE_ORIGINAL == image_base64.encode()
    assert result.IMAGE32 == image32_base64.encode()
