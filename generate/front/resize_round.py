from PIL import Image, ImageOps
from pathlib import Path
import numpy as np

BASE_DIR = str(Path(__file__).resolve().parent) + '/resources'


def resize_round(img):
    img = img[0][0]

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
    return [new_img], new_img