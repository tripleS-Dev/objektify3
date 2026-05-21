
import gradio as gr
from PIL import Image, ImageOps
from pathlib import Path
from utils import paste_correctly, svg_to_pil, resize_keep_ratio, remove_signature_background, color_change, \
    crop_transparent_padding

BASE_DIR = str(Path(__file__).resolve().parent) + '/resources'


img_format = ('.png', '.webp', 'jpg', 'jpeg')


def top(color_json, top_logo: str, scale: int, remove_bg: bool):
    if not top_logo:
        return gr.Image(), gr.Image(), color_json


    top_logo_preview_img = Image.open(f'{BASE_DIR}/top_logo_preview.png')


    if top_logo.lower().endswith(img_format):
        top_logo = Image.open(top_logo)

        if top_logo.size[1] >= top_logo.size[0]:
            top_logo = resize_keep_ratio(top_logo, target_height=int(117*scale/100))
        else:
            top_logo = resize_keep_ratio(top_logo, target_height=int(50*scale/100))

        if remove_bg:
            top_logo = crop_transparent_padding(remove_signature_background(top_logo))

        top_logo_pil = top_logo

    elif top_logo.lower().endswith('.svg'):
        top_logo_pil = svg_to_pil(top_logo, target_height=int(117*scale/100))


    else:
        return gr.Image(), gr.Image(), color_json

    top_logo_pil = color_change(top_logo_pil, '#FFFFFF')
    backside = paste_correctly(top_logo_preview_img, (57, 151), top_logo_pil)

    color_json['top_logo'] = True


    return backside, top_logo_pil, color_json

def qr(color_json, qr_logo):
    if not qr_logo:
        return gr.Image(), gr.Image(), color_json


    if qr_logo.lower().endswith(img_format):
        qr_logo_pil = Image.open(qr_logo)

        qr_logo_pil = ImageOps.fit(qr_logo_pil, (80, 80))


    elif qr_logo.lower().endswith('.svg'):
        qr_logo_pil = svg_to_pil(qr_logo, target_width=80)

    else:
        return gr.Image(), gr.Image(), color_json





    qr_logo_preview_img = Image.open(f'{BASE_DIR}/qr_logo_preview.png')

    backside = paste_correctly(qr_logo_preview_img, (235, 157), qr_logo_pil)

    color_json['qr_logo'] = True


    return backside, qr_logo_pil, color_json


def side(color_json, side_logo, scale: int, remove_bg: bool):
    if not side_logo:
        return gr.Image(), gr.Image(), color_json

    if side_logo.lower().endswith(img_format):
        side_logo = Image.open(side_logo)

        if remove_bg:
            side_logo = crop_transparent_padding(remove_signature_background(side_logo))

        side_logo_pil = resize_keep_ratio(side_logo, target_height=40+scale)

    elif side_logo.lower().endswith('.svg'):
        side_logo_pil = svg_to_pil(side_logo, target_height=40+scale)
    else:
        return gr.Image(), gr.Image(), color_json



    qr_logo_preview_img = Image.open(f'{BASE_DIR}/side_logo_preview.png')

    side_logo_pil = color_change(side_logo_pil, '#FFFFFF')


    side_logo_temp = side_logo_pil.rotate(270, expand=True)

    backside = paste_correctly(qr_logo_preview_img, (qr_logo_preview_img.size[0]-37-side_logo_temp.size[0], qr_logo_preview_img.size[1]-152-side_logo_temp.size[1]), side_logo_temp)

    color_json['side_logo'] = True

    return backside, side_logo_pil, color_json