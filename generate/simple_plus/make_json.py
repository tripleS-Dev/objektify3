import json
import os

import gradio as gr
import time
from generate.back.back import generate_back
from generate.front import generate_front
from PIL import PngImagePlugin, Image
from pathlib import Path
from utils import get_kr_time, paste_correctly, get_json, simple2advanced, save_log_json


def make_json(temp_id, cache_id, source_image, artist, season=None, class_=None, background_color=None, text_color=None, member=None, unit=None, numbering_state=None, number=None, alphabet=None, serial=None, qr_code=None):

    gen_started_at_epoch_us = time.time_ns() // 1_000  # Unix epoch in microseconds


    if cache_id:
        safe_name = Path(str(cache_id)).name
        cache_dir = Path("./cache")

        for suffix in ("objektify-front-", "objektify-back-", "objektify-combined-"):
            path = cache_dir / f"{suffix}{safe_name}.png"
            try:
                path.unlink()
            except FileNotFoundError:
                pass


    raws = [artist, season, class_, member, unit, numbering_state, number, alphabet, serial, qr_code]


    if not numbering_state:
        number = ''
        alphabet = ''
        serial = ''

    if qr_code is None:
        qr_code = 'https://objektify.xyz/'



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
            "qr_code": qr_code,
            "qr_caption": 'https://objektify.xyz'
        },
        "raw": raws,
        "generation": {
            "started_at_epoch_us": gen_started_at_epoch_us,
            "timezone": "Asia/Seoul",
        }
    }



    #print(data)
    krtime = get_kr_time()

    # 메타데이터로 저장할 인수들을 딕셔너리로 구성 (source_image 제외)
    meta_dict = {
        "artist": str(artist),
        "season": str(season),
        "class": str(class_),
        "member": str(member),
        "numbering_state": str(numbering_state),
        "number": str(number),
        "alphabet": str(alphabet),
        "serial": str(serial),
        "qr_code": str(qr_code)
    }

    save_log_json(data, temp_id, f"{krtime}.json")


    img = front(meta_dict, krtime, source_image, data, side_logo_img, side_bar_img)
    img2 = back(meta_dict, krtime, data, back_img, side_logo_img, top_logo_img, sign_img, sign_position, qr_logo_img)

    combined = combine(meta_dict, krtime, img, img2)

    advanced_components = simple2advanced(data, sign_img, sign_position[0], sign_position[1], qr_logo_img, top_logo_img, side_logo_img, side_bar_img, back_img)


    return [krtime, [img, img2, combined], gr.DownloadButton(value=img), gr.DownloadButton(value=img2), gr.DownloadButton(value=combined), img, img2, combined] + advanced_components



def front(meta_dict, krtime, source_image, data, side_logo_img, side_bar_img):
    img = generate_front(source_image, data, side_logo_img, side_bar_img)
    meta = PngImagePlugin.PngInfo()
    meta.add_text('objektify', 'V3')
    meta.add_text('aspect', 'front')

    # meta_dict 내용 추가
    if meta_dict:
        for key, value in meta_dict.items():
            meta.add_text(key, value)


    img.save(f'./cache/objektify-front-{krtime}.png', pnginfo=meta)  # save to cache
    return f'./cache/objektify-front-{krtime}.png'


def back(meta_dict, krtime, data, back_img, side_logo_img, top_logo_img, sign_img, sign_position, qr_logo_img):
    img = generate_back(data, back_img, side_logo_img, top_logo_img, sign_img, sign_position, qr_logo_img)
    meta = PngImagePlugin.PngInfo()
    meta.add_text('objektify', 'V3')
    meta.add_text('aspect', 'back')
    meta.add_text('mode', 'simple')

    # meta_dict 내용 추가
    if meta_dict:
        for key, value in meta_dict.items():
            meta.add_text(key, value)


    img.save(f'./cache/objektify-back-{krtime}.png', pnginfo=meta)  # save to cache
    return f'./cache/objektify-back-{krtime}.png'


def combine(meta_dict, krtime, img, img2):

    img = Image.open(img)
    img2 = Image.open(img2)


    combined_width = img2.size[0] + img.size[0]  # Horizontal concatenation
    combined_height = max(img2.size[1], img.size[1])

    combined = Image.new('RGBA', (combined_width, combined_height), (0, 0, 0, 0))

    combined = paste_correctly(combined, (0, 0), img)
    combined = paste_correctly(combined, (img.size[0], 0), img2)

    meta = PngImagePlugin.PngInfo()
    meta.add_text('objektify', 'V3')
    meta.add_text('aspect', 'both')
    meta.add_text('mode', 'simple')

    # meta_dict 내용 추가
    if meta_dict:
        for key, value in meta_dict.items():
            meta.add_text(key, value)


    combined.save(f'./cache/objektify-combined-{krtime}.png', pnginfo=meta)  # save to cache
    return f'./cache/objektify-combined-{krtime}.png'






