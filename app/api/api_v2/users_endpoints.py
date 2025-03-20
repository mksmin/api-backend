# import lib
import json

# import from lib
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, FileResponse
from pathlib import Path

# import from modules

router = APIRouter()
