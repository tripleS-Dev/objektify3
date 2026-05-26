import json
import os
from typing import Any

import classes
from PIL import Image, ImageOps
from config import ARTIST_DIR
from utils import get_json


class Config:
    def __init__(self, artist, member):
        config_path = os.path.join(ARTIST_DIR, artist, 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

        if self.config.get('side_logo', None):
            side_logo_path = os.path.join(ARTIST_DIR, artist, 'side_logo.png')
            self.side_logo_img = Image.open(side_logo_path)
        else:
            self.side_logo_img = None

        if self.config.get('top_logo', None):
            top_logo_path = os.path.join(ARTIST_DIR, artist, 'top_logo.png')
            self.top_logo_img = Image.open(top_logo_path)
        else:
            self.top_logo_img = None

        if get_json(self.config, f'members.{member}.sign', False, bool):
            sign_img_path = os.path.join(ARTIST_DIR, artist, 'signs', f'{member}.png')
            self.sign_img = Image.open(sign_img_path)
            self.sign_position = get_json(self.config, f'members.{member}.position', None, tuple)
        else:
            self.sign_img = None
            self.sign_position = None

def img_upload(
        img: Any|None,
        name: str|None = None,
        group: str|None = None,
        group_logo: Image.Image|None = None,
        background_color: str|None = '#FFFFFF',
        text_color: str|None = '#000000',
        number: str|None = None,
        alphabet: str|None = '',
        serial: int|str|None = None,
        class_: str|None = None,
        season: str|None = None,
        qr_code: str|None = None,
        qr_caption: str|None = None,
):


    objekt = classes.Objekt(text_color, background_color, name, group, number, alphabet, serial)
    if group_logo:
        objekt.set_group_logo_side(group_logo)

    if img:
        img = open_img(img)
        objekt.front.round_corner()
        objekt.front.resize()

        objekt.front.set_raw_img(img)




    if group:
        config = Config(group)

        if config.side_logo_img:
            objekt.front.set_group_logo_side(config.side_logo_img)

        objekt.front.draw_sidebar()

        if any([number, serial]):
            objekt.front.draw_serial()

        objekt.front.attach_sidebar()


        objekt.back(class_, season).attach_layout().draw_text().attach_qr_code()
        if config.top_logo_img:
            objekt.back.attach_top_logo(config.top_logo_img)

        if config.sign_img:
            objekt.back.attach_sign(config.sign_img, config.sign_position)

    return objekt

import gradio as gr

if __name__ == "__main__":
    objekt = img_upload(None, 'JooBin', number='100', group='tripleS', alphabet='Z', serial='1')
    #objekt.front.show()

def open_config(artist: str):
    config_path = os.path.join('./artists', artist, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    return config



def open_img(img):
    if len(img) >= 4 and "objektify-combined" in img[2][0]:
        if len(img) >= 5:
            gr.Info("You can only upload one image.", duration=5)

        img = img[3][0]


    elif len(img) >= 2:
        gr.Info("You can only upload one image.", duration=5)
        img = img[0][0]
    else:
        img = img[0][0]

    img = Image.open(img)

    try:
        img = ImageOps.exif_transpose(img) #https://github.com/python-pillow/Pillow/issues/4703
    except ZeroDivisionError:
        img = img.rotate(270, expand=True) #There is an issue with vertically taken photos in the Kiwi Browser on Android, so I manually rotate them.


    return img


