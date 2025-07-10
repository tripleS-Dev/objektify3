import json
import os

import gradio as gr

from generate.back.back import generate_back
from generate.front import generate_front
from PIL import PngImagePlugin, Image

from utils import get_kr_time, paste_correctly, get_json


def make_json(input_image_raw, artist, season=None, class_=None, member=None, numbering_state=None, number=None, alphabet=None, serial=None, qr_code=None):

    if not artist:
        return


    if not numbering_state:
        number = ''
        alphabet = ''
        serial = ''

    if qr_code is None:
        qr_code = 'https://objektify.xyz/'


    config_path = os.path.join('./artists', artist, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if config.get('side_logo', None):
        side_logo_path = os.path.join('./artists', artist, 'side_logo.png')
        side_logo_img = Image.open(side_logo_path)
    else:
        side_logo_img = None

    if not input_image_raw:
        if config.get('default', None):
            input_image_path = os.path.join('./artists', artist, 'default.png')
            input_image_raw = Image.open(input_image_path)

    if get_json(config, f'members.{member}.sign', False):
        sign_path = os.path.join('./artists', artist, f'signs/{member}.png')
        sign_img = Image.open(sign_path)

        if get_json(config, f'members.{member}.position', None):
            sign_position = get_json(config, f'members.{member}.position', (59, 1020))
        else:
            x = int((453-sign_img.size[0])/2 +59)
            y = int((311-sign_img.size[1])/2 +1020)
            sign_position = (x, y)
    else:
        sign_img = None
        sign_position = None

    if get_json(config, f'top_logo', False):
        top_logo_path = os.path.join('./artists', artist, f'top_logo.png')
        top_logo_img = Image.open(top_logo_path)
    else:
        top_logo_img = None


    background_color = config.get('seasons', {}).get(season, {}).get(class_, None)
    if not background_color:
        if config.get('default_color', None):
            background_color = config.get('default_color')
        else:
            background_color = '#FFFFFF'
    else:
        background_color = background_color[0]

    text_color = config.get('seasons', {}).get(season, {}).get(class_, None)
    if not text_color:
        text_color = '#000000'
    else:
        text_color = text_color[1]

    if not background_color.startswith('#'):
        side_bar_img_path = os.path.join('./artists', artist, background_color, 'front.png')
        side_bar_img = Image.open(side_bar_img_path)

        back_img_path = os.path.join('./artists', artist, background_color, 'back.png')
        back_img = Image.open(back_img_path)

    else:
        side_bar_img = None
        back_img = None


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
        },
        "text_area": {
            "class": class_,
            "season": season,
            "qr_code": qr_code
        }
    }


    #print(data)
    krtime = get_kr_time()
    img = front(krtime, input_image_raw, data, side_logo_img, side_bar_img)
    img2 = back(krtime, data, back_img, side_logo_img, top_logo_img, sign_img, sign_position)

    combined = combine(krtime, img, img2)


    return [[img, img2, combined], gr.DownloadButton(value=img)]



def front(krtime, input_image_raw, data, side_logo_img, side_bar_img):
    img = generate_front(input_image_raw, data, side_logo_img, side_bar_img)
    meta = PngImagePlugin.PngInfo()
    meta.add_text('objektify', 'V3')
    meta.add_text('side', 'front')
    img.save(f'./cache/objektify-front-{krtime}.png', pnginfo=meta)  # save to cache
    return f'./cache/objektify-front-{krtime}.png'


def back(krtime, data, back_img, side_logo_img, top_logo_img, sign_img, sign_position):
    img = generate_back(data, back_img, side_logo_img, top_logo_img, sign_img, sign_position)
    meta = PngImagePlugin.PngInfo()
    meta.add_text('objektify', 'V3')
    meta.add_text('side', 'front')
    img.save(f'./cache/objektify-back-{krtime}.png', pnginfo=meta)  # save to cache
    return f'./cache/objektify-back-{krtime}.png'


def combine(krtime, img, img2):

    img = Image.open(img)
    img2 = Image.open(img2)


    combined_width = img2.size[0] + img.size[0]  # Horizontal concatenation
    combined_height = max(img2.size[1], img.size[1])

    combined = Image.new('RGBA', (combined_width, combined_height), (0, 0, 0, 0))

    combined = paste_correctly(combined, (0, 0), img)
    combined = paste_correctly(combined, (img.size[0], 0), img2)

    meta = PngImagePlugin.PngInfo()
    meta.add_text('objektify', 'V3')
    meta.add_text('side', 'front')
    combined.save(f'./cache/objektify-combined-{krtime}.png', pnginfo=meta)  # save to cache
    return f'./cache/objektify-combined-{krtime}.png'






