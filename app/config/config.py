"""
This module load environment and read .env file
"""

import os
import logging
import asyncio
from dotenv import load_dotenv



logger = logging.getLogger(__name__)



def get_tokens(name_of_token: str) -> str:
    """
    The function accept name of token as str, load .env file and find token

    :param name_of_token: (str) name of token
    :return: (str) token
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        return os.getenv(name_of_token)
    else:
        print('No .env file found')
