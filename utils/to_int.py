
from typing import Any

def to_int(*t: Any):
    return tuple(round(x) for x in t)