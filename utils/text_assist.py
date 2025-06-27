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



def hex2rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))