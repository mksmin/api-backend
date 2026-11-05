import datetime as dt
from typing import Annotated
from typing import Self

from fastapi import APIRouter
from fastapi import Form
from fastapi import HTTPException
from fastapi import status
from fastapi.concurrency import run_in_threadpool
from fastapi.params import Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi_csrf_protect import CsrfProtect
from pwdlib import PasswordHash
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field
from pydantic import field_validator
from pydantic import model_validator
from sqlalchemy import Row
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from auth import jwt_helper
from core.database import User
from core.database.db_helper import db_helper
from core.database.users import PasswordCredential

router = APIRouter()
passwords = PasswordHash.recommended()


class CredentialsForm(BaseModel):
    email: EmailStr = Field(
        max_length=254,
    )
    password: str = Field(
        min_length=8,
        max_length=1024,
    )

    @field_validator(
        "email",
        mode="before",
    )
    @classmethod
    def normalize_email(
        cls,
        value: str,
    ) -> str:
        return value.strip().lower()


class LoginCredentialsForm(CredentialsForm): ...


class CreateCredentialsForm(CredentialsForm):
    password_confirm: str

    @model_validator(
        mode="after",
    )
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            msg = "Passwords doesn't match"
            raise ValueError(msg)
        return self


class UserUnavailableError(Exception): ...


class CredentialAlreadyExistsError(Exception): ...


class CredentialService:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def authenticate_user(
        self,
        credentials: LoginCredentialsForm,
    ) -> User | None:
        stmt = (
            select(
                User,
                PasswordCredential,
            )
            .join(
                PasswordCredential,
                PasswordCredential.user_id == User.id,
            )
            .where(
                func.lower(PasswordCredential.email) == credentials.email,
            )
        )

        row: Row[User, PasswordCredential] | None = (
            await self.session.execute(stmt)
        ).one_or_none()
        if row is None:
            return None

        user: User = row[0]
        credential: PasswordCredential = row[1]

        if user.deleted_at is not None:
            return None
        if credential.email_verified_at is None:
            return None

        valid = await run_in_threadpool(
            passwords.verify,
            credentials.password,
            credential.password_hash,
        )
        return user if valid else None

    async def create_user_credentials(
        self,
        user_id: int,
        user_credentials_in: CreateCredentialsForm,
    ) -> None:
        user = await self.session.get(User, user_id)
        if user is None or user.deleted_at is not None:
            raise UserUnavailableError

        existing = await self.session.get(
            PasswordCredential,
            user_id,
        )
        if existing is not None:
            raise CredentialAlreadyExistsError

        password_hash = await run_in_threadpool(
            passwords.hash,
            user_credentials_in.password,
        )

        self.session.add(
            PasswordCredential(
                user_id=user_id,
                email=user_credentials_in.email,
                password_hash=password_hash,
                email_verified_at=dt.datetime.now(dt.UTC),
            ),
        )

        try:
            await self.session.commit()
        except IntegrityError as exc:
            await self.session.rollback()
            raise CredentialAlreadyExistsError from exc


@router.post(
    "/create-credentials",
)
async def create_credentials(
    request: Request,
    user_credentials_in: Annotated[
        CreateCredentialsForm,
        Form(),
    ],
    user_id: Annotated[
        int,
        Depends(
            jwt_helper.strict_validate_access_token,
        ),
    ],
    session: Annotated[
        AsyncSession,
        Depends(
            db_helper.session_getter,
        ),
    ],
    csrf_protect: Annotated[
        CsrfProtect,
        Depends(),
    ],
) -> JSONResponse:
    await csrf_protect.validate_csrf(request)
    try:
        await CredentialService(session).create_user_credentials(
            user_id,
            user_credentials_in,
        )
    except UserUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from exc
    except CredentialAlreadyExistsError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Credential already exists or email used",
        ) from exc

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "id": user_id,
            "email": user_credentials_in.email,
        },
    )


@router.post(
    "/authenticate",
)
async def authenticate_user(
    _request: Request,
    user_credentials: Annotated[
        LoginCredentialsForm,
        Form(),
    ],
    session: Annotated[
        AsyncSession,
        Depends(
            db_helper.session_getter,
        ),
    ],
) -> JSONResponse:
    user = await CredentialService(session).authenticate_user(
        user_credentials,
    )

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "message": "User not found!",
            },
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "id": user.id,
            "username": user.username,
            "uuid": str(user.uuid),
            "first_name": user.first_name,
            "last_name": user.last_name,
        },
    )
