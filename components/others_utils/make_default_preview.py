from copy import deepcopy
from pathlib import Path
from PIL import Image, ImageOps

from utils import color_change, paste_correctly, apply_mask, extend_right_edge, extend_right_edge_inpaint, resize_objekt

img_dir = f'{Path(__file__).resolve().parent.parent.parent}/components/others_utils/resources/color_preview/'

def make_default_preview(default_color_side, default_color_text, default_img, batch_type):
    base = Image.open(img_dir+'background.png')
    side = Image.open(img_dir+'side.png')
    text = Image.open(img_dir+'text.png')


    if default_img:
        if batch_type == 'Center of viewport':
            base = resize_objekt(default_img, (1083, 1673), 32)
        else:
            base = ImageOps.fit(default_img, (1083, 1673))
    #print(base.size)

    base = base.convert('RGBA')
    base = apply_mask(base, f'{Path(__file__).resolve().parent.parent.parent}/generate/front/resources/blank_alpha.png')
    base_save = deepcopy(base)

    side = color_change(side, default_color_side)
    text = color_change(text, default_color_text)

    base = paste_correctly(base, (965, 97), side)
    base = paste_correctly(base, (985, 133), text)

    return base, base_save