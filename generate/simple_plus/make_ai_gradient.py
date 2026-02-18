from ai.comfyui_api.ai_gradient import run_gradient_ws_image
import gradio as gr
from PIL import Image

from utils import apply_mask
from pathlib import Path


BASE_DIR = str(Path(__file__).resolve().parent) + '/resources/'

def make_ai_gradient(ai_color, ai_color_shape, seed):
    if ai_color == []:
        gr.Info('Please select at least one AI color.')
        return

    if ai_color_shape == 'Gradient':
        shape = 'wavy, '
    elif ai_color_shape == 'Wave':
        shape = 'wave, '
    else:
        shape = 'wavy'

    prompt = shape + ', '.join(ai_color) + ', gradient'

    print(prompt)

    img = run_gradient_ws_image(seed, prompt)

    sidebar_img, back_img = resize_and_split(img)


    sidebar_img = apply_mask(sidebar_img, f'{BASE_DIR}/sidebar.png')
    back_img = apply_mask(back_img, f'{BASE_DIR}/back.png')

    return img, sidebar_img, back_img



def resize_and_split(img: Image.Image):
    # 1) 1158 x 1673으로 리사이즈
    img = img.resize((1083+118, 1673), Image.Resampling.LANCZOS)

    # 2) 좌표 기준으로 분할 (PIL crop: right, lower는 제외)
    # (0,0)~(75,1673)  => (left=0, upper=0, right=76, lower=1673)
    sidebar_img = img.crop((0, 0, 118, 1673)).rotate(90, expand=True)

    # (76,0)~(1158,1673) => (left=76, upper=0, right=1158, lower=1673)
    back_img = img.crop((118, 0, 1083+118, 1673))

    return sidebar_img, back_img