import json
import os
from typing import Any


#from . import classes
import classes
from PIL import Image, ImageOps
from config import ARTIST_DIR
from utils import get_json

def open_config(artist: str):
    config_path = os.path.join('./artists', artist, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    return config



def open_img(img):

    if isinstance(img, Image.Image):
        return img

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

class Config:
    def __init__(self, artist, member, season, class_):
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

        color = get_json(self.config, f'seasons.{season}.{class_}', False, tuple)
        if color:

            if color[0].startswith('#'):
                self.text_color = color[1]
                self.background_color = color[0]

            else:
                self.text_color = None
                self.background_color = None

        else:
            self.text_color = None
            self.background_color = None

        self.season_display = get_json(self.config, f'seasons.{season}.display', season, str)



def img_upload(
        objekt: classes.Objekt=None,
        img: Any=None,
        name: Any=None,
        group: str|None = None,
        background_color: str='#FFFFFF',
        text_color: str='#000000',
        number: str|None = None,
        alphabet: str= '',
        serial: int|str = None,
        class_: str|None = None,
        season: str|None = None,
        qr_code: str|None = None,
        qr_caption: str|None = None,
):
    if not objekt:
        objekt = classes.Objekt(text_color, background_color, name, group, number, alphabet, serial)
        if img:
            img = open_img(img)
            objekt.front.set_raw_img(img)
            objekt.front.resize()
            objekt.front.round_corner()

    print(number)
    objekt.meta = classes.ObjektMeta(
            artist_name=name,
            group_name=group,
            number=number,
            alphabet=alphabet,
            serial=serial,
        )


    if group:
        config = Config(group, name, season, class_)

        if config.text_color:
            objekt.theme = classes.ObjektTheme(
                text_color=config.text_color,
                background_color=config.background_color,
            )
        else:
            objekt.theme = classes.ObjektTheme(
                text_color=text_color,
                background_color=background_color,
            )


        if any([number, serial]):
            objekt.draw_sidebar().draw_serial()


        if config.side_logo_img:
            objekt.set_group_logo_side(config.side_logo_img)


        objekt.front.attach_sidebar()


        objekt.back(class_, config.season_display).reset().attach_layout().draw_text().attach_qr_code().draw_sidebar()
        if config.top_logo_img:
            objekt.back.attach_top_logo(config.top_logo_img)

        if config.sign_img:
            objekt.back.attach_sign(config.sign_img, config.sign_position)

    return objekt, [objekt.back.back_ready_img, objekt.front_img]

import gradio as gr

if __name__ == "__main__":
    img = Image.new('RGB', (2000,1000), (200,100,50))
    objekt, *_ = img_upload(None, img, 'KimLip', number='100', group='tripleS', alphabet='Z', class_='First', season="Atom01")
    objekt.front.show()
    objekt.back.show()




