import random
import string
from uuid import uuid4


def short_id(length=5):
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )
