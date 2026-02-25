import logging
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from fastapi import Depends
from types_aiobotocore_s3.client import S3Client

from app_exceptions.exceptions import FailedToUploadS3FileError
from config import settings

log = logging.getLogger(__name__)


@dataclass
class S3Config:
    aws_access_key_id: str
    aws_secret_access_key: str
    endpoint_url: str


class S3Service:
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        endpoint_url: str,
        bucket_name: str,
    ) -> None:
        self.config = S3Config(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            endpoint_url=endpoint_url,
        )
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def get_client(self) -> AsyncGenerator[S3Client]:
        async with self.session.create_client(
            "s3",
            aws_access_key_id=self.config.aws_access_key_id,
            aws_secret_access_key=self.config.aws_secret_access_key,
            endpoint_url=self.config.endpoint_url,
        ) as client:
            yield client

    async def upload_file(
        self,
        file_bytes: bytes,
        file_ext: str = "jpg",
        target_dir: str | None = None,
    ) -> str:
        filename = f"{uuid.uuid4()}.{file_ext.lower()}"
        object_key = f"{target_dir.rstrip('/')}/{filename}" if target_dir else filename

        object_key = object_key.removeprefix("/")

        try:
            async with self.get_client() as client:
                await client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=file_bytes,
                )
        except ClientError as e:
            message_error = "Failed to upload file to s3"
            raise FailedToUploadS3FileError(message_error) from e
        return object_key

    def get_url(
        self,
        object_name: str,
    ) -> str:
        base_url = self.config.endpoint_url
        if not base_url.endswith("/"):
            base_url += "/"
        return f"{base_url}{self.bucket_name}/{object_name}"

    async def delete_file(
        self,
        object_name: str,
    ) -> bool:
        try:
            async with self.get_client() as client:
                await client.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                )
        except ClientError:
            message_error = "Failed to delete file from s3"
            log.exception(message_error)
            return False
        return True


async def get_s3_service() -> S3Service:
    return S3Service(
        access_key=settings.s3.access_key,
        secret_key=settings.s3.secret_key,
        endpoint_url=settings.s3.endpoint_url,
        bucket_name=settings.s3.bucket_name,
    )


GetS3Service = Annotated[
    S3Service,
    Depends(get_s3_service),
]
