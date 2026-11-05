import datetime as dt

from pwdlib import PasswordHash
from sqlalchemy import Row
from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from app_exceptions.exceptions import CredentialAlreadyExistsError
from app_exceptions.exceptions import UserUnavailableError
from core.database import User
from core.database.users import PasswordCredential
from schemas.user_credentials import CreateCredentialsForm
from schemas.user_credentials import CredentialsReadSchema
from schemas.user_credentials import LoginCredentialsForm

passwords = PasswordHash.recommended()


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

    async def get_user_email(
        self,
        user_id: int,
    ) -> CredentialsReadSchema:
        user = await self.session.get(User, user_id)
        if user is None or user.deleted_at is not None:
            raise UserUnavailableError

        stmt = select(
            PasswordCredential.email,
            PasswordCredential.email_verified_at,
        ).where(
            PasswordCredential.user_id == user_id,
        )
        row = (await self.session.execute(stmt)).one_or_none()
        if row is None:
            return CredentialsReadSchema(
                email=None,
                email_confirmed=False,
            )

        return CredentialsReadSchema(
            email=row.email,
            email_confirmed=row.email_verified_at is not None,
        )
