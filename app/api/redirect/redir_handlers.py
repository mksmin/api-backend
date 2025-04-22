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


@router.api_route(
    "/projects",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def project_redirect(request: Request):
    path = f"{path_mapping['users']}projects"
    if request.query_params:
        path = f"{path_mapping['users']}projects?{request.query_params}"
    return RedirectResponse(url=path, status_code=307)


@router.api_route(
    "/projects/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    include_in_schema=False,
)
async def project_nested_redirect(request: Request, path: str):
    query = f"?{request.query_params}" if request.query_params else ""
    return RedirectResponse(
        url=f"{path_mapping['users']}projects/{path}{query}", status_code=307
    )


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
