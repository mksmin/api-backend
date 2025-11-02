from typing import TypedDict, cast

from fastapi.requests import Request

FLASH_MESSAGES_KEY = "_flashed_messages"


class Message(TypedDict):
    message: str
    category: str


def flash(
    request: Request,
    message: str,
    category: str = "info",
) -> None:
    if FLASH_MESSAGES_KEY not in request.session:
        request.session[FLASH_MESSAGES_KEY] = []

    request.session[FLASH_MESSAGES_KEY].append(
        Message(
            message=message,
            category=category,
        ),
    )


def get_flashed_messages(
    request: Request,
) -> list[Message]:
    return cast(
        "list[Message]",
        request.session.pop(FLASH_MESSAGES_KEY, []),
    )
