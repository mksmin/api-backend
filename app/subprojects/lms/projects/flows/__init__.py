from fastapi import APIRouter

from subprojects.lms.projects.flows.create import router as flows_create_router
from subprojects.lms.projects.flows.details import router as flows_details_router
from subprojects.lms.projects.flows.list import router as flows_list_router

router = APIRouter(
    prefix="/{project_uuid}/flows",
)

router.include_router(
    flows_list_router,
)
router.include_router(
    flows_create_router,
)
router.include_router(
    flows_details_router,
)
