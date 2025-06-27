from PIL import Image, ImageDraw
from pathlib import Path

from utils import color_change, get_json, paste_correctly, text_draw

BASE_DIR = str(Path(__file__).resolve().parent) + '/resources/'

def generate_back(json) -> Image.Image:
    backside, layout, inside = open_images()

    inside = color_change(inside, get_json(json, 'appearance.background_color', '#000000'))
    layout = color_change(layout, get_json(json, 'appearance.text_color', '#000000'))


    backside = paste_correctly(backside, (0,0), inside)

    backside = paste_correctly(backside, (0,0), layout)


    draw = ImageDraw.Draw(backside)


    text_draw(draw, (55, 471), 'Helvetica_Neue_LT_Std_65_Medium-4.otf', 126, get_json(json, 'artist.name', ''), get_json(json, 'appearance.text_color', '#000000'))

    return backside


def open_images():
    backside = Image.open(BASE_DIR + 'blank_alpha.png')
    layout = Image.open(BASE_DIR + 'layout.png')

    # backside = color_change(backside, '#FFFFFF')

    inside = Image.open(BASE_DIR + 'inside.png')
    return backside, layout, inside

if __name__ == '__main__':
    data = {
        "artist": {
            "name": "SeoYeon",
            "group": "tripleS"
        },
        "appearance": {
            "background_color": "#FF00FF",
            "text_color": "#000000",
        },
        "identifiers": {
            "number": 100,
            "alphabet": None,
            "serial": 1
        }
    }

    generate_back(data).save('fdd.png')