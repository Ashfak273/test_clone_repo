import re
from uuid import UUID
import random
import string
import request
import os
import httpx
import time

def with_exponential_backoff(metadata, connection_config, max_attempts=5):
    attempt = 0
    backoff_time = 3 

    while attempt < max_attempts:
        try:
            rs = box_op(metadata, connection_config)
            return rs
        except Exception as e:
            logging.error("Error: %s Attempt: %s Backoff Wait: %s File ID: %s", e, attempt, backoff_time, metadata["id"])
            time.sleep(backoff_time)
            attempt += 1
            backoff_time *= 2
    raise Exception("Max retry attempts reached for Box SDK.")


def contains_uuid(s):
    uuid_regex = re.compile(
        r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[1-5][a-fA-F0-9]{3}-[89abAB][a-fA-F0-9]{3}-[a-fA-F0-9]{12}$'
    )
    
    if uuid_regex.match(s):
        try:
            uuid_obj = UUID(s)
            return True
        except ValueError:
            return False

    return False

def generate_random_string(length: int = 5) -> str:
    letters = string.ascii_letters  # Contains both lowercase and uppercase letters
    return ''.join(random.choice(letters) for _ in range(length))
