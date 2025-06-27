import json
import os

import gradio as gr

from generate.front import generate_front
from config import season_color
from PIL import PngImagePlugin, Image

from utils import get_kr_time


def make_json(input_image_raw, artist, season=None, class_=None, member=None, numbering_state=None, number=None, alphabet=None, serial=None):
    if not numbering_state:
        number = ''
        alphabet = ''
        serial = ''






    config_path = os.path.join('./artists', artist, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if config.get('side_logo', None):
        side_logo_path = os.path.join('./artists', artist, 'side_logo.png')
        side_logo_img = Image.open(side_logo_path)
    else:
        side_logo_img = None



    background_color = config.get('seasons', {}).get(season, {}).get(class_, None)
    if not background_color:
        background_color = '#FFFFFF'
    else:
        background_color = background_color[0]

    text_color = config.get('seasons', {}).get(season, {}).get(class_, None)
    if not text_color:
        text_color = '#000000'
    else:
        text_color = text_color[1]

    if not background_color.startswith('#'):
        side_bar_img_path = os.path.join('./artists', artist, background_color)
        side_bar_img = Image.open(side_bar_img_path)
    else:
        side_bar_img = None

    data = {
        "artist": {
            "name": member,
            "group": artist
        },
        "appearance": {
            "background_color": background_color,
            "text_color": text_color,
        },
        "identifiers": {
            "number": number,
            "alphabet": alphabet,
            "serial": serial if serial else None
        }
    }


    print(data)
    img = generate_front(input_image_raw, data, side_logo_img, side_bar_img)

    meta = PngImagePlugin.PngInfo()
    meta.add_text('objektify', 'V3')
    meta.add_text('side', 'front')
    krtime = get_kr_time()
    img.save(f'./cache/objektify-{krtime}.png', pnginfo=meta)  # save to cache

    return [img, gr.DownloadButton(value=f'./cache/objektify-{krtime}.png')]