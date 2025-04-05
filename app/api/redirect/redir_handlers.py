from fastapi import APIRouter, Header, Body, Request
from fastapi.responses import JSONResponse, RedirectResponse

router = APIRouter()

actual_version = "/api/v2/"

path_mapping = {
    "users": actual_version + "users/",
}


@router.get("/statistics/", include_in_schema=False)
async def get_statistics(token=Header()) -> RedirectResponse:
    return RedirectResponse(url=f"{path_mapping['users']}statistics", status_code=308)


@router.post("/registration", include_in_schema=False)
async def registration(data=Body()):
    return RedirectResponse(url=f"{path_mapping['users']}registration", status_code=308)


@router.post("/get_token/{user_id}", include_in_schema=False)
async def get_token(user_id: int):
    return RedirectResponse(
        url=f"{path_mapping['users']}get_token/{user_id}", status_code=308
    )


@router.get("/projects", include_in_schema=False)
@router.post("/projects", include_in_schema=False)
async def project_redirect(request: Request):
    query_params = request.query_params
    redirect_url = f"{path_mapping['users']}projects?{query_params}"
    return RedirectResponse(redirect_url, status_code=307)


@router.delete("/projects/{project_id}", include_in_schema=False)
async def create_project(project_id: int):
    return RedirectResponse(
        url=f"{path_mapping['users']}projects/{project_id}", status_code=308
    )


@router.post("/create_task", include_in_schema=False)
async def rabbit_task_create(data=Body()):
    return RedirectResponse(url=f"{path_mapping['users']}create_task", status_code=308)


@router.post("/tasks", include_in_schema=False)
async def rabbit_task_create(data=Body()):
    return RedirectResponse(url=f"{path_mapping['users']}tasks", status_code=308)


# @router.get("/auth", include_in_schema=False)
# @router.post("/auth", include_in_schema=False)
# async def project_redirect(request: Request):
#     query_params = request.query_params
#     redirect_url = f"{path_mapping['users']}auth?{query_params}"
#     return RedirectResponse(redirect_url, status_code=307)
