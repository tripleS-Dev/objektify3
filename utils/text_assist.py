from typing import Optional, Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def text_draw(
    draw: ImageDraw.Draw,
    position: tuple,
    font: str,
    font_size: int,
    txt: str,
    txt_color: Optional[Union[str, tuple]] = None,
    variation: Optional[str] = None,
    pos: int = 0
):
    if txt == '':
        return

    match pos:
        case 0:

            y_offset = (1/5)*font_size + 1
            offset = (0,y_offset)

            font = ImageFont.truetype(f"{BASE_DIR}/fonts/{font}", font_size)

            if variation: font.set_variation_by_name(variation)
            if not txt_color: txt_color = (255, 255, 255)  # Default to white
            if isinstance(txt_color, str): txt_color = hex2rgb(txt_color)

            draw.text((position[0]-offset[0], position[1]-offset[1]), txt, fill=txt_color, font=font)
            txt_bbox = font.getbbox(txt)

            txt_width = txt_bbox[2] - txt_bbox[0]
            txt_height = txt_bbox[3] - txt_bbox[1]
            return int(txt_width), int(txt_height)

        case 1:
            font = ImageFont.truetype(f"{BASE_DIR}/fonts/{font}", font_size)

            # Apply variation if specified
            if variation: font.set_variation_by_name(variation)

            # Set default text color to white if not provided
            if not txt_color: txt_color = (255, 255, 255)  # Default to white
            if isinstance(txt_color, str): txt_color = hex2rgb(txt_color)

            # Calculate text size
            txt_bbox = font.getbbox(txt)
            txt_width = txt_bbox[2] - txt_bbox[0]
            txt_height = txt_bbox[3] - txt_bbox[1]

            # Calculate top-left position to center the text
            top_left_x = position[0] - txt_width / 2
            top_left_y = position[1] - txt_height / 2

            # Draw the text
            draw.text((top_left_x, top_left_y), txt, fill=txt_color, font=font)

            return int(txt_width), int(txt_height)
        case 2:
            offset = (0, 7)

            font = ImageFont.truetype(f"{BASE_DIR}/fonts/{font}", font_size)

            if variation: font.set_variation_by_name(variation)
            if not txt_color: txt_color = (255, 255, 255)  # Default to white
            if isinstance(txt_color, str): txt_color = hex2rgb(txt_color)

            txt_bbox = font.getbbox(txt)
            txt_size = (txt_bbox[2] - txt_bbox[0], txt_bbox[3] - txt_bbox[1])
            draw.text((position[0] - txt_size[0] - offset[0], position[1] - offset[1]), txt, fill=txt_color, font=font)
            return txt_size
    return None


from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent


def text_size(
    font: str,
    font_size: int,
    txt: str,
    variation: Optional[str] = None,
):
    font = ImageFont.truetype(f"{BASE_DIR}/fonts/{font}", font_size)

    if variation: font.set_variation_by_name(variation)


    txt_bbox = font.getbbox(txt)

    txt_width = txt_bbox[2] - txt_bbox[0]
    txt_height = txt_bbox[3] - txt_bbox[1]
    return int(txt_width), int(txt_height)



import re

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

def _parse_chan(v: str) -> int:
    v = v.strip()
    if v.endswith("%"):
        return _clamp255(float(v[:-1]) * 255.0 / 100.0)
    return _clamp255(float(v))

def hex2rgb(color: str):
    """
    입력:
      - '#RRGGBB' / '#RGB'
      - 'rgb(r,g,b)' / 'rgba(r,g,b,a)'
      - 'rgb(r g b)' 같은 공백 구분도 허용
    반환: (r, g, b) 0~255 int 튜플
    """
    color = color.strip()

    # rgb/rgba 처리
    if color.lower().startswith("rgb"):
        m = _RGBA_RE.match(color)
        if not m:
            raise ValueError(f"Invalid rgb/rgba() format: {color}")
        r = _parse_chan(m.group("r"))
        g = _parse_chan(m.group("g"))
        b = _parse_chan(m.group("b"))
        return (r, g, b)

    # hex 처리
    h = color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"Invalid hex format: {color}")

    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
