from fastapi import APIRouter

from subprojects.lms.projects.participants.list import router as participant_list_router

router = APIRouter(
    prefix="/{project_uuid}/participants",
)

router.include_router(
    participant_list_router,
)
