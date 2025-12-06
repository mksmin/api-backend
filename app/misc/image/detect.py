from app_exceptions.exceptions import ImageFormatError


def detect_image_type(
    data: bytes,
) -> str:
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"

    if data.startswith(b"\xff\xd8\xff"):
        return "jpeg"

    message_error = "Unknown or unsupported image type"
    raise ImageFormatError(message_error)
