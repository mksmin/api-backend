import logging

import aiohttp
from fastapi import status
from PIL import Image

from app_exceptions.exceptions import (
    ImageFetchError,
    ImageFormatError,
    ImageSizeError,
)
from misc.image.security import _is_safe_url
from misc.image.types import (
    AIOHTTP_TIMEOUT,
    ALLOWED_CONTENT_TYPES,
    MAX_BYTES,
    MAX_DIMENSION,
)

log = logging.getLogger(__name__)

Image.MAX_IMAGE_PIXELS = MAX_DIMENSION * MAX_DIMENSION


async def fetch_image_stream(
    url: str,
) -> bytes:
    if not _is_safe_url(url):
        message_error = f"Unsafe URL: {url}"
        raise ImageFetchError(message_error)

    timeout = aiohttp.ClientTimeout(total=AIOHTTP_TIMEOUT)
    try:
        async with aiohttp.ClientSession(
            timeout=timeout,
        ) as session, session.get(url) as response:
            if response.status != status.HTTP_200_OK:
                message_error = f"HTTP {response.status}"
                raise ImageFetchError(message_error)

            content_type = (
                response.headers.get("content-type", "").split(";")[0].lower().strip()
            )
            if content_type and content_type not in ALLOWED_CONTENT_TYPES:
                message_error = f"Disallowed content type: {content_type}"
                raise ImageFormatError(message_error)

            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > MAX_BYTES:
                message_error = "Image is too large"
                raise ImageSizeError(message_error)

            total = 0
            chunks = []
            async for chunk in response.content.iter_chunked(64 * 1024):
                total += len(chunk)
                if total > MAX_BYTES:
                    message_error = "Image too large"
                    raise ImageSizeError(message_error)
                chunks.append(chunk)

            data = b"".join(chunks)
            if not data:
                message_error = "No data received"
                raise ImageFetchError(message_error)

            return data

    except aiohttp.ClientError as e:
        message_error = f"Failed to fetch image: {e}"
        log.warning(message_error)
        raise ImageFetchError(message_error) from e
