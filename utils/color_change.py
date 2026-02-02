import re
import numpy as np
from PIL import Image

_RGBA_RE = re.compile(
    r"""^rgba?\(\s*
        (?P<r>[\d.]+%?)\s*[, ]\s*
        (?P<g>[\d.]+%?)\s*[, ]\s*
        (?P<b>[\d.]+%?)
        (?:\s*(?:[,/]\s*|\s+)\s*(?P<a>[\d.]+%?))?
        \s*\)$
    """,
    re.IGNORECASE | re.VERBOSE,
)

def _clamp255(x: float) -> int:
    return max(0, min(255, int(round(x))))

def _parse_rgb(s: str) -> tuple[int, int, int]:
    s = s.strip()

    # 1) rgba(...) / rgb(...)
    if s.lower().startswith("rgb"):
        m = _RGBA_RE.match(s)
        if not m:
            raise ValueError(f"Invalid rgb/rgba() format: {s}")

        def parse_chan(v: str) -> int:
            v = v.strip()
            if v.endswith("%"):
                # 0–100% -> 0–255
                return _clamp255(float(v[:-1]) * 255.0 / 100.0)
            return _clamp255(float(v))

        r = parse_chan(m.group("r"))
        g = parse_chan(m.group("g"))
        b = parse_chan(m.group("b"))
        return (r, g, b)

    # 2) hex (#RGB, #RRGGBB)
    h = s.lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    if len(h) != 6:
        raise ValueError(f"Invalid hex format: {s}")

    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return (r, g, b)

def color_change(img: Image.Image, new_hex: str) -> Image.Image:
    """
    img     : RGBA Pillow 이미지 객체
    new_hex : '#RRGGBB' / '#RGB' / 'rgb(r,g,b)' / 'rgba(r,g,b,a)'
    반환값  : 알파는 유지하고 RGB만 새 색으로 바꾼 새 RGBA 이미지
    """
    arr = np.asarray(img.convert("RGBA")).copy()
    new_rgb = _parse_rgb(new_hex)
    arr[..., :3] = new_rgb  # alpha 채널(arr[..., 3])은 그대로 둠
    return Image.fromarray(arr, mode="RGBA")
