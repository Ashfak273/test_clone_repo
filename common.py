import re
from uuid import UUID
import random
import string
import request
import os

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
