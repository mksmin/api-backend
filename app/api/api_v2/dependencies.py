from uuid import UUID

from app_exceptions import InvalidUUIDError


def validate_uuid_str(
    project_uuid: str,
) -> UUID:
    try:
        return UUID(project_uuid)
    except ValueError as e:
        raise InvalidUUIDError from e
