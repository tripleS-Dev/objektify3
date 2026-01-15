import json

def get_meta(img):
    info = {}
    for k, v in (img.info or {}).items():
        # JSON 직렬화 불가한 값은 문자열로
        try:
            json.dumps(v)
            info[k] = v
        except Exception:
            info[k] = str(v)

    return info