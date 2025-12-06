import asyncio
import io

from PIL import Image

from app_exceptions.exceptions import (
    ImageFormatError,
    ImageSizeError,
)
from misc.image.detect import detect_image_type
from misc.image.types import (
    ALLOWED_FORMATS,
    MAX_DIMENSION,
)


async def validate_image_bytes(
    data: bytes,
) -> tuple[str, tuple[int, int]]:
    detected_type = detect_image_type(data)

    def _open_image(
        buf: bytes,
    ) -> tuple[str | None, tuple[int, int]]:
        bio = io.BytesIO(buf)
        img = Image.open(bio)
        img.verify()

        bio.seek(0)
        img2 = Image.open(bio)
        return img2.format, img2.size

    try:
        fmt, size = await asyncio.to_thread(_open_image, data)
    except Exception as e:
        message_error = f"Invalid image: {e}"
        raise ImageFormatError(message_error) from e

    fmt_lower = fmt.lower() if fmt else ""

    if fmt_lower == "jpg":
        fmt_lower = "jpeg"

    if fmt_lower not in ALLOWED_FORMATS:
        message_error = f"Unsupported image format: {fmt_lower}"
        raise ImageFormatError(message_error)

    if fmt_lower != detected_type:
        message_error = f"Format mismatch: header={detected_type}, actual={fmt_lower}"
        raise ImageFormatError(message_error)

    w, h = size
    if w <= 0 or h <= 0 or w > MAX_DIMENSION or h > MAX_DIMENSION:
        message_error = f"Invalid image dimensions: {w}x{h}"
        raise ImageSizeError(message_error)

    return fmt_lower, size
