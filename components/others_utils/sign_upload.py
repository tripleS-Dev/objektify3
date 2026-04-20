import gradio as gr

from PIL import Image
from utils import remove_signature_background, paste_correctly, color_change, crop_transparent_padding
from io import BytesIO
from pathlib import Path
from typing import List
import cairosvg


BASE_DIR = str(Path(__file__).resolve().parent) + '/resources/'

blank_img = Image.new('RGB', size=(1,1), color='black')


def sign_upload(color_json, members, members_radio, sign_save: List[Image.Image], file: str, x_offset: float, y_offset: float, size: int, remove_bg: bool, progress_checkbox: List[str] | None):
    if not file:
        return None, None, None, None


    file_type = file.split('.')[-1].lower()

    match file_type:
        case 'png' | 'jpeg' | 'jpg' | 'webp':
            img_raw = fit_image(
                crop_transparent_padding(
                    Image.open(file) if not remove_bg else remove_signature_background(file)
                )
            , size)

            img, position = composit_preview(img_raw, x_offset, y_offset)
            img = img.crop((0, 797, 1083, 729+797))

            btn = gr.Button(interactive=False, variant='secondary')
        case 'svg':
            img_raw = fit_image(svg_to_rgba_array(file), size)
            img, position = composit_preview(img_raw, x_offset, y_offset)
            img = img.crop((0, 797, 1083, 729+797))

            btn = gr.Button(interactive=False, variant='secondary')
        case _:
            gr.Info('Unknown file type')
            img = None
            img_raw = None
            position = None
            btn = gr.Button(interactive=True, variant='primary')



    def sign_save_init():
        sign_save = []
        for i in range(len(members)):
            sign_save.append(blank_img)
        return sign_save
    if not sign_save:
        sign_save = sign_save_init()
    if not len(sign_save) == len(members):
        sign_save = sign_save_init()

    selected_index = members.index(members_radio)

    sign_save[selected_index] = img_raw

    progress_checkbox.append(members_radio)

    color_json['members'][members_radio] = {}
    color_json['members'][members_radio]['sign'] = True
    color_json['members'][members_radio]['position'] = [position[0], position[1]]


    return btn, img, gr.Gallery(value=sign_save), gr.CheckboxGroup(value=progress_checkbox), color_json



def remove_partial_transparency(img: Image.Image) -> Image.Image:
    """
    완전투명(alpha=0)은 그대로 두고,
    반투명(alpha=1~254)은 alpha를 255로 바꿔 불투명하게 만든다.
    완전불투명(alpha=255)은 그대로 둔다.
    """
    img = img.convert("RGBA")
    out = img.copy()

    data = []
    for r, g, b, a in out.getdata():
        if a <= 30:
            data.append((r, g, b, 0))      # 완전투명 유지
        elif 30 < a < 255:
            data.append((r, g, b, 255))    # 반투명 -> 불투명
        else:
            data.append((r, g, b, 255))    # 원래 불투명
    out.putdata(data)
    return out


def sign_resize(img: Image.Image, multiple: int):
    width, height = img.size

    new_width = int(width*multiple/100)
    new_height = int(height*multiple/100)

    img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)
    return img

def composit_preview(img: Image.Image, x_offset: float, y_offset: float):
    #img = remove_partial_transparency(img)


    img = color_change(img, '#FFFFFF')



    base = Image.open(BASE_DIR+'preview.png')


    position = (int(68+((436-img.size[0])/2)+x_offset), int(1030+((293-img.size[1])/2)+y_offset))
    img = paste_correctly(base, position, img)

    return img, position


def sign_change(file: str):
    if not file:
        return gr.Button(variant='secondary', interactive=False), gr.Image(value=None)


    file_type = file.split('.')[-1].lower()


    if file_type == 'svg':
        return gr.Button(variant='secondary', interactive=False), None

    return gr.Button(variant='primary', interactive=True), None


"""def remove_bg_btn_click(file, x_offset, y_offset, size):
    file_type = file.split('.')[-1].lower()

    #if file_type == 'webp':
    #    file = Image.open(file).convert('RGBA')
    #    print('webp')

    img = fit_image(
        crop_transparent_padding(
            remove_signature_background(file)
        )
    )
    img = composit_preview(img, x_offset, y_offset, size)
    return gr.Button(variant='secondary', interactive=False), gr.Image(value=img)"""



def fit_image(img: Image.Image, multiple, max_size=(436, 293)) -> Image.Image:
    """
    Pillow 이미지 객체를 max_size 안에 비율 유지하며 맞춤.

    Args:
        img: PIL.Image.Image 객체
        max_size: (max_width, max_height)

    Returns:
        크기 조절된 새 PIL.Image.Image 객체
    """
    max_w, max_h = max_size
    w, h = img.size

    scale = min(max_w / w, max_h / h)
    new_size = (round(w * scale*multiple/100), round(h * scale*multiple/100))


    #width, height = img.size

    #new_width = int(width*multiple/100)
    #new_height = int(height*multiple/100)

    #img = img.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)

    return img.resize(new_size, resample=Image.Resampling.LANCZOS)



def svg_to_rgba_array(
    svg_input: str | bytes | Path,
    width: int = 436,
    height: int = 293,
) -> Image.Image:
    """
    SVG를 RGBA PIL.Image 객체로 변환한다.
    """
    if isinstance(svg_input, Path) or (
        isinstance(svg_input, str) and Path(svg_input).exists()
    ):
        svg_bytes = Path(svg_input).read_bytes()
    elif isinstance(svg_input, str):
        svg_bytes = svg_input.encode("utf-8")
    elif isinstance(svg_input, bytes):
        svg_bytes = svg_input
    else:
        raise TypeError("svg_input은 SVG 문자열, bytes, 또는 파일 경로여야 합니다.")

    png_bytes = cairosvg.svg2png(
        bytestring=svg_bytes,
        output_width=width,
        output_height=height,
    )

    return Image.open(BytesIO(png_bytes)).convert("RGBA")




if __name__ == "__main__":
    sign_upload('dsd.png')