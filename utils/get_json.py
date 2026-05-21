from pydash import get
from typing import Callable, Any

_MISSING = object()

def get_json(json, path: str, default, output_type: Callable[[Any], Any] | None = None):
    value = get(json, path, _MISSING)

    if value is _MISSING:
        return default

    if value == default:
        return value

    if output_type is None:
        return value

    try:
        return output_type(value)
    except (ValueError, TypeError):
        return default