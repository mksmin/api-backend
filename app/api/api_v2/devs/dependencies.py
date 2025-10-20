import logging
from io import StringIO
from typing import Annotated, Any

import pandas as pd
from fastapi import File, HTTPException, UploadFile, status

from api.api_v2.auth import access_token_helper as token_utils
from core.crud import GetCRUDService
from schemas import UserCreateSchema

log = logging.getLogger(__name__)


async def create_token_by_user_id(
    user_id: int,
) -> dict[str, Any]:
    if not isinstance(user_id, int):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="User ID must be an integer",
        )
    return await token_utils.sign_jwt_token(user_id)


async def read_and_parse_csv(
    file: Annotated[UploadFile, File()],
    crud_service: GetCRUDService,
) -> None:
    if file.filename and not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are allowed",
        )
    try:
        # Read the CSV file
        content = await file.read()
        csv_string = StringIO(content.decode("utf-8"))
        df = pd.read_csv(csv_string)

        # Check if the CSV has the data
        if df.empty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="CSV file is empty",
            )

        # Convert to list of dicts
        data = df.to_dict(orient="records")

        for user in data:
            user.pop("id", None)
            user.pop("created_at", None)
            user.pop("copmetention", None)

            await crud_service.user.create_user(
                user_create=UserCreateSchema.model_validate(user),
            )

    except pd.errors.EmptyDataError as ed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV file is empty or invalid",
        ) from ed
    except pd.errors.ParserError as pe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error parsing CSV file",
        ) from pe
