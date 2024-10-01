"""
This module load environment and read .env file
"""

import os
import logging
from dotenv import load_dotenv
from datetime import datetime


class CustomFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    green = "\x1b[32;20m"
    reset = "\x1b[0m"
    format = "[%(asctime)s] %(levelname)s: %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, '%Y/%m/%d %H:%M:%S')
        return formatter.format(record)


# FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Настраиваем логгер, используя созданный форматтер.
console_handler = logging.StreamHandler()
formatter = CustomFormatter()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


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
