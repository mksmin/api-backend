LOGIN_REDIRECT_PATHS = frozenset(
    {
        "/profile",
        "/projects",
        "/affirmations",
        "/lms",
    },
)


def safe_login_redirect(
    value: str | None = None,
    *,
    default: str = "/profile",
) -> str:
    candidate = default if value is None else value
    if candidate == "/lms" or candidate.startswith("/lms/"):
        return "/lms/"

    if candidate.removesuffix("/") in LOGIN_REDIRECT_PATHS:
        return candidate
    return default
