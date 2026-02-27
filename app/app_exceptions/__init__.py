from app_exceptions.exceptions import AuthBaseError as AuthBaseError
from app_exceptions.exceptions import (
    FailedToUploadS3FileError as FailedToUploadS3FileError,
)
from app_exceptions.exceptions import (
    FiledToDeleteS3FileError as FiledToDeleteS3FileError,
)
from app_exceptions.exceptions import ImageFetchError as ImageFetchError
from app_exceptions.exceptions import ImageFormatError as ImageFormatError
from app_exceptions.exceptions import ImageSizeError as ImageSizeError
from app_exceptions.exceptions import InvalidPayloadError as InvalidPayloadError
from app_exceptions.exceptions import InvalidSignatureError as InvalidSignatureError
from app_exceptions.exceptions import InvalidUUIDError as InvalidUUIDError
from app_exceptions.exceptions import (
    ProjectAlreadyExistsError as ProjectAlreadyExistsError,
)
from app_exceptions.exceptions import ProjectNotFoundError as ProjectNotFoundError
from app_exceptions.exceptions import (
    RabbitMQServiceUnavailableError as RabbitMQServiceUnavailableError,
)
from app_exceptions.exceptions import UnknownBotAuthError as UnknownBotAuthError
from app_exceptions.exceptions import (
    UnsupportedClientTypeError as UnsupportedClientTypeError,
)
from app_exceptions.exceptions import UserAlreadyExistsError as UserAlreadyExistsError
from app_exceptions.exceptions import UserNotFoundError as UserNotFoundError
