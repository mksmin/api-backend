# import libraries
import os
# import binascii
import time
import jwt

# import from libraries
from decouple import config

# local load env
# from dotenv import load_dotenv
# dirname_file = os.path.dirname(__file__)
# dirname_step = os.path.dirname(dirname_file)
# dirname_next_step = os.path.dirname(dirname_step)
# dotenv_path = os.path.abspath(os.path.join(dirname_next_step, 'config/.env'))
# load_dotenv(dotenv_path)

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")


async def token_response(token: str) -> dict:
    return {
        "access_token": token
    }


async def sign_jwt(user_id: str) -> dict:
    payload = {
        "user_id": user_id,
        "expires": time.time() + 3600000
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return await token_response(token)


async def decode_jwt(token: str) -> dict:
    error_message = {"success": False, "message": {"error": "invalid token"}}
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return {"success": True} if decoded_token['expires'] > time.time() else error_message
    except:
        return error_message
