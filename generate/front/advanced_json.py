import os

from generate.back.back import generate_back
from PIL import PngImagePlugin, Image

from utils import get_kr_time


def advanced_json(input_image_raw, advanced_components = None):
    main_color, text_color, name, group_text, class_, season, season_outline, number, alphabet, serial, sign, sign_scale, sign_position_x, sign_position_y, qr_code, qr_logo, qr_caption, sidebar_logo, top_logo, sidebar, back_layout = advanced_components

    data = {
        "artist": {
            "name": name,
            "group": group_text
        },
        "appearance": {
            "background_color": main_color,
            "text_color": text_color,
        },
        "identifiers": {
            "number": number,
            "alphabet": alphabet,
            "serial": serial if serial else None
        },
        "text_area": {
            "class": class_,
            "season": f"{season}/{season_outline}",
            "qr_code": qr_code,
            "qr_caption": qr_caption
        }
    }

    krtime = get_kr_time()


    if not main_color.startswith('#'):
        side_bar_img_path = os.path.join('./artists', artist, background_color, 'front.png')
        side_bar_img = Image.open(side_bar_img_path)

        back_img_path = os.path.join('./artists', artist, background_color, 'back.png')
        back_img = Image.open(back_img_path)



    img2 = back(krtime, data, back_img, side_logo_img, top_logo_img, sign_img, sign_position)

    #back pattern advanced and simple color change and gradient

def back(krtime, data, back_img, side_logo_img, top_logo_img, sign_img, sign_position):
    img = generate_back(data, back_img, side_logo_img, top_logo_img, sign_img, sign_position)
    meta = PngImagePlugin.PngInfo()
    meta.add_text('objektify', 'V3')
    meta.add_text('side', 'front')
    img.save(f'./cache/objektify-back-{krtime}.png', pnginfo=meta)  # save to cache
    return f'./cache/objektify-back-{krtime}.png'