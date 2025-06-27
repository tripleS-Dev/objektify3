from pydash import get


def get_json(json, path: str, default):
    if get(json, path, default):
        return get(json, path, default)
    else:
        return default