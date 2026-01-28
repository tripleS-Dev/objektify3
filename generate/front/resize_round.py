from PIL import Image, ImageOps
from pathlib import Path
import numpy as np

from generate.front.make_json import make_json  # Corrected import

from utils import get_kr_time, copy_image_to_folder
import secrets

import gradio as gr

BASE_DIR = str(Path(__file__).resolve().parent) + '/resources'


def resize_round(img, cache_id=None, input_image_raw=None, artist=None, season = None, class_ = None, member = None, unit=None, numbering_state = None, number = None, alphabet = None, serial = None, qr_code = None):
    if len(img) >= 4 and "objektify-combined" in img[2][0]:
        if len(img) >= 5:
            gr.Info("You can only upload one image.", duration=5)

        img = img[3][0]


    elif len(img) >= 2:
        gr.Info("You can only upload one image.", duration=5)
        img = img[0][0]
    else:
        img = img[0][0]

    krtime = get_kr_time()

    source_image = str(img)  # 원본 이미지 경로
    logs_dir = Path('logs')
    logs_dir.mkdir(parents=True, exist_ok=True)
    folder_name = f"{krtime}"
    folder_path = logs_dir / folder_name
    folder_path.mkdir(parents=True, exist_ok=True)

    copy_image_to_folder(source_image, folder_path)


    img = Image.open(img)

    try:
        img = ImageOps.exif_transpose(img) #https://github.com/python-pillow/Pillow/issues/4703
    except ZeroDivisionError:
        img = img.rotate(270, expand=True) #There is an issue with vertically taken photos in the Kiwi Browser on Android, so I manually rotate them.


    blank_alpha = Image.open(f'{BASE_DIR}/blank_alpha.png')
    blank_alpha = blank_alpha.convert("RGBA")
    img = ImageOps.fit(img, (1083, 1673))
    img = img.convert("RGBA")
    blank_alpha = blank_alpha.resize(img.size)

    # Convert to numpy arrays
    img_array = np.array(img)
    blank_alpha_array = np.array(blank_alpha)

    # Extract alpha channels
    img_alpha = img_array[:, :, 3]
    blank_alpha_alpha = blank_alpha_array[:, :, 3]

    # Create mask where blank_alpha's alpha is less than img's
    mask = blank_alpha_alpha < img_alpha

    # Combine alphas
    new_alpha = np.where(mask, blank_alpha_alpha, img_alpha)

    # Update the alpha channel in the image array
    img_array[:, :, 3] = new_alpha

    # Create new image from the array
    new_img = Image.fromarray(img_array)

    blank = [None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]

    if artist:
        a = make_json(folder_name, cache_id, new_img, artist, season, class_, member, unit, numbering_state, number, alphabet, serial, qr_code)
        cache_id, img_card, download_front, download_back, download_combine, raws = a[0], a[1], a[2], a[3], a[4], a[5]
        return [folder_name, cache_id, img_card, new_img, download_front, download_back, download_combine, raws]+ a[6:]
    else:
        return [folder_name, '', [new_img], new_img, None, None, None, None, None, None]+ blank