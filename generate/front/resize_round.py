from PIL import Image, ImageOps
from pathlib import Path
import numpy as np

from generate.front.make_json import make_json  # Corrected import

BASE_DIR = str(Path(__file__).resolve().parent) + '/resources'


def resize_round(img, input_image_raw=None, artist=None, season=None, class_=None, member=None, numbering_state=None, number=None, alphabet=None, serial=None):
    img = img[0][0]



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



    if artist:
        a = make_json(new_img, artist, season, class_, member, number, alphabet, serial)
        img_card, download_btn = a[0], a[1]
        return img_card, new_img, download_btn
    else:
        return [new_img], new_img, None