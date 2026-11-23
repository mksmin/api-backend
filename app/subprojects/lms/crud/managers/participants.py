from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.lms import LMSParticipant
from schemas.lms.participants import LMSParticipantsCreateSchema


class LMSParticipantsManager:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def get_by_email(
        self,
        email: str,
    ) -> LMSParticipant | None:
        stmt = select(
            LMSParticipant,
        ).where(
            func.lower(
                LMSParticipant.email,
            )
            == email.strip().lower(),
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        participant_in: LMSParticipantsCreateSchema,
    ) -> LMSParticipant:
        participant = LMSParticipant(
            **participant_in.model_dump(),
        )
        self.session.add(participant)
        return participant
