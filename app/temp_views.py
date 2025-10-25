from fastapi import APIRouter

router = APIRouter()

user_projects = {
    "projects": [
        {
            "title": "Project 1",
            "description": "This is a description of project 1",
            "uuid": "1234567890",
        },
        {
            "title": "Project 2",
            "description": "This is a description of project 2",
            "uuid": "1234567890",
        },
        {
            "title": "Атом-лаб. Весна 2025",
            "description": "Без описания",
            "created_at": "2025-03-27T13:14:33.079241",
            "uuid": "2e05a7c7-73a1-4c84-90dd-ca2a72466db2",
        },
    ],
}


# @router.get(
#     "/user",
#     name="user-projects:list",
# )
# async def get_user_profile(
#     request: Request,
# ) -> HTMLResponse:
#     context = {}
#     context.update(
#         {
#             "request": request,
#             "user": {
#                 "photo_url": "https://cdn4.telesco.pe/file/bj2m8LW8_hk8FIHx0VRVjbRxTphEgX-jWc6K3tvQkEPHBXEURvQYwwAmgIpOJFsnq0HXZU5GBs9aAe9CWtkPxo9BePtdJygmNr0lqYI6ISkW2pjUjDIkxGdu89rNYA3y4IObY5bOoF40mUOHPj92IywxntGYP5BBmxwSEceqGHtv79DnDZuTYBS-5v4o5PcPIqEWAdW92lAQKnr8--OkYoPwqIIOeSNv2dn44nmjcraXXliSmjELSGjQFa2YKtPWb0fhqxwslfKLufJv7CBj_K8_mHv4KbhJBoSFTvdc8XhU0LzTUQlXU5oOx6UYIavU4X9_H7_z2E9jOc6FsjRZaw.jpg",
#                 "first_name": "John",
#                 "last_name": "Doe",
#                 "username": "johndoe",
#             },
#             "settings": {
#                 "count_tasks": "--",
#                 "time_send": "--",
#             },
#         },
#     )
#     context.update(**user_projects)
#     return templates.TemplateResponse(
#         "project/list.html",
#         context=context,
#     )
#
#
# @router.get(
#     "/user/{uuid}",
#     name="user-projects:detail",
# )
# async def get_user_project_detail(
#     request: Request,
#     uuid: str,
# ) -> HTMLResponse:
#     context = {}
#     context.update(
#         {
#             "request": request,
#         }
#     )
#     for project in user_projects["projects"]:
#         if project["uuid"] == uuid:
#             context.update(
#                 {
#                     "project": project,
#                 }
#             )
#             break
#
#     return templates.TemplateResponse(
#         "project/details.html",
#         context=context,
#     )
