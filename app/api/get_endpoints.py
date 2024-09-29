import os

from app.config.config import app
from fastapi.responses import JSONResponse, FileResponse

cwd = os.getcwd()
dirname = os.path.dirname(__file__)
path_dirname = os.path.dirname(dirname)
cwd_project_path = os.path.normpath(os.path.dirname(path_dirname))


@app.get("/")
async def index_page():
    index_html = os.path.join(cwd_project_path, "html/index.html")
    return FileResponse(index_html)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = os.path.join(cwd_project_path, "favicon.ico")
    return FileResponse(favicon_path)


@app.get("/robots.txt", include_in_schema=False)
async def robots():
    robots_path = os.path.join(cwd_project_path, "robots.txt")
    return FileResponse(robots_path)


@app.get('/html/{name_media}', include_in_schema=False)
async def html_path(name_media: str):
    media_path = os.path.join(path_dirname, "html/", name_media)
    not_found_404 = os.path.join(path_dirname, 'html/404.html')
    file_exists = os.path.exists(str(media_path))
    if not file_exists:
        return FileResponse(not_found_404)
    else:
        return FileResponse(media_path)


@app.get('/test/', include_in_schema=False)
async def test():
    pass