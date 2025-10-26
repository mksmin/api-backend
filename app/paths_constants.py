from fastapi.templating import Jinja2Templates

from core.config import BASE_DIR, settings
from misc.flash_messages import get_flashed_messages

FRONTEND_DIR_PATH = (
    BASE_DIR.parent.parent / "api-frontend"
    if settings.run.dev_mode
    else BASE_DIR.parent.parent / "frontend"
)

HTML_DIR = FRONTEND_DIR_PATH / "public"
STATIC_DIR = FRONTEND_DIR_PATH / "static"
not_found_404 = HTML_DIR / "404.html"

templates = Jinja2Templates(directory=FRONTEND_DIR_PATH / "templates")
templates.env.globals[get_flashed_messages.__name__] = get_flashed_messages
