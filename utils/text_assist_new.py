from typing import Optional, Union, Literal, Tuple
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parent

XAlign = Literal["left", "right", "center"]
YAlign = Literal["top", "bottom", "center", "cap_center"]
Align = Union[XAlign, Tuple[XAlign, YAlign], list[str]]


def normalize_align(align: Align) -> Tuple[str, str]:
    if isinstance(align, str):
        if align not in ("left", "right", "center"):
            raise ValueError(f"Invalid align: {align}")

        y_align = "center" if align == "center" else "top"
        return align, y_align

    if len(align) == 1:
        return normalize_align(align[0])

    if len(align) != 2:
        raise ValueError("align must be a string or [x_align, y_align]")

    x_align, y_align = align

    if x_align not in ("left", "right", "center"):
        raise ValueError(f"Invalid x align: {x_align}")
    if y_align not in ("top", "bottom", "center", "cap_center"):
        raise ValueError(f"Invalid y align: {y_align}")

    return x_align, y_align


def get_position(
    align: Align,
    position,
    img_size: Tuple[int, int],
    font,
    txt: str,
) -> Tuple[int, int]:
    x_align, y_align = normalize_align(align)

    txt_bbox = font.getbbox(txt)
    x1, y1, x2, y2 = txt_bbox

    if x_align == "left":
        x = position[0]
    elif x_align == "right":
        x = img_size[0] - position[0] - x2
    else:
        x = position[0] - (x1 + x2) / 2

    if y_align == "top":
        y = position[1]
    elif y_align == "bottom":
        y = img_size[1] - position[1] - y2
    elif y_align == "cap_center":
        cap_bbox = font.getbbox("H")
        cap_y1, cap_y2 = cap_bbox[1], cap_bbox[3]
        y = position[1] - (cap_y1 + cap_y2) / 2
    else:
        # 기존 center 유지: 실제 txt bbox 기준 중앙
        y = position[1] - (y1 + y2) / 2

    return int(x), int(y)


import json

with open(f"{BASE_DIR}/fonts/offsets.json", "r", encoding="utf-8") as f:
    font_offset = json.load(f)



def text_draw(
    img_size: Tuple[int, int],
    draw: ImageDraw.Draw,
    position: tuple,
    font_name: str,
    font_size: int,
    txt: str,
    txt_color: Optional[Union[str, tuple]] = None,
    variation: Optional[str] = None,
    align: Align = "left",
    measure_only=False
) -> Tuple[int, int]:

    if font_offset.get(font_name, None):
        if font_offset[font_name].get('type', None) == "byFontsize":
            if font_offset[font_name].get(align):
                position = (position[0], position[1] + round(font_size/font_offset[font_name][align][1]))



    font = ImageFont.truetype(f"{BASE_DIR}/fonts/{font_name}", font_size)

    if variation:
        font.set_variation_by_name(variation)

    if not txt_color:
        txt_color = (255, 255, 255)

    if isinstance(txt_color, str):
        txt_color = hex2rgb(txt_color)

    if not measure_only:
        position_fixed = get_position(align, position, img_size, font, txt)
        draw.text(position_fixed, txt, fill=txt_color, font=font)

    txt_bbox = font.getbbox(txt)
    txt_width = txt_bbox[2] - txt_bbox[0]
    txt_height = txt_bbox[3] - txt_bbox[1]

    return int(txt_width), int(txt_height)


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


def hex2rgb(color: str) -> Tuple[int, int, int]:
    color = color.strip()

    if color.lower().startswith("rgb"):
        m = _RGBA_RE.match(color)
        if not m:
            raise ValueError(f"Invalid rgb/rgba() format: {color}")

        r = _parse_chan(m.group("r"))
        g = _parse_chan(m.group("g"))
        b = _parse_chan(m.group("b"))

        return (r, g, b)

    h = color.lstrip("#")

    if len(h) == 3:
        h = "".join(c * 2 for c in h)

    if len(h) != 6:
        raise ValueError(f"Invalid hex format: {color}")

    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


if __name__ == "__main__":
    img = Image.open("offset.png")
    size = img.size
    draw = ImageDraw.Draw(img)

    font = "AritaBuriKR-SemiBold.ttf"
    font_size = 96

    text_draw(
        size,
        draw,
        (0, 0),
        font,
        font_size,
        "left",
        (255, 0, 0),
        align="left",
    )

    text_draw(
        size,
        draw,
        (size[0] / 2, size[1] / 2),
        font,
        font_size,
        "center",
        (255, 0, 0),
        align="center",
    )

    text_draw(
        size,
        draw,
        (1, 605),
        font,
        font_size,
        "right",
        (255, 0, 0),
        align="right",
    )

    text_draw(
        size,
        draw,
        (1, size[1] / 2),
        font,
        font_size,
        "right center",
        (0, 255, 0),
        align=["right", "center"],
    )

    text_draw(
        size,
        draw,
        (size[0] / 2, 20),
        font,
        font_size,
        "center top",
        "#0000ff",
        align=["center", "top"],
    )

    text_draw(
        size,
        draw,
        (size[0] / 2, 20),
        font,
        font_size,
        "center bottom",
        "rgb(255, 128, 0)",
        align=["center", "bottom"],
    )

    img.show()
