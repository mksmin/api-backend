# import libraries
import os
import time
import jwt

# import from libraries
from decouple import config


JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


async def token_response(token: str) -> dict:
    return {
        "message": token
    }


async def sign_jwt(user_id: int) -> dict:
    payload = {
        "user_id": str(user_id),
        "expires": time.time() + 3600000
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return await token_response(token)


async def decode_jwt(token: str) -> dict:
    error_message = {"message": {"success": False, "error": "invalid token"}}
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"message": {"success": True}} if decoded_token['expires'] > time.time() else error_message
    except Exception as e:
        return error_message
