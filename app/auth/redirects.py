LOGIN_REDIRECT_PATHS = frozenset(
    {
        "/profile",
        "/projects",
        "/affirmations",
    },
)


def safe_login_redirect(
    value: str | None = None,
    *,
    default: str = "/profile",
) -> str:
    candidate = default if value is None else value
    if candidate.removesuffix("/") in LOGIN_REDIRECT_PATHS:
        return candidate
    return default
