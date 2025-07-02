from PIL import Image, ImageDraw
from pathlib import Path

from utils import color_change, get_json, paste_correctly, text_draw

BASE_DIR = str(Path(__file__).resolve().parent) + '/resources/'

def generate_back(json, back_img=None, side_logo=None, top_logo=None) -> Image.Image:

    backside, layout, inside = open_images()


    if back_img:
        inside = back_img
    else:
        inside = color_change(inside, get_json(json, 'appearance.background_color', '#000000'))


    layout = color_change(layout, get_json(json, 'appearance.text_color', '#000000'))

    if top_logo:
        top_logo = color_change(top_logo, get_json(json, 'appearance.text_color', '#000000'))
        backside = paste_correctly(backside, (57, 151), top_logo)


    backside = paste_correctly(backside, (0,0), inside)

    backside = paste_correctly(backside, (0,0), layout)


    draw = ImageDraw.Draw(backside)


    text_draw(draw, (55, 471), 'Helvetica_Neue_LT_Std_65_Medium-4.otf', 126, get_json(json, 'artist.name', ''), get_json(json, 'appearance.text_color', '#000000'))
    text_draw(draw, (55, 471+216), 'Helvetica_Neue_LT_Std_65_Medium-4.otf', 126, get_json(json, 'text_area.class', ''), get_json(json, 'appearance.text_color', '#000000'))
    text_draw(draw, (55, 471+216+216), 'Helvetica_Neue_LT_Std_65_Medium-4.otf', 126, get_json(json, 'text_area.season', ''), get_json(json, 'appearance.text_color', '#000000'))



    sidebar = Image.open(BASE_DIR + 'sidebar.png')

    if side_logo:
        side_logo = color_change(side_logo, get_json(json, 'appearance.text_color', '#000000'))
        sidebar = paste_correctly(sidebar, (1478 - 55 - side_logo.size[0], 37), side_logo)

    else:
        draw = ImageDraw.Draw(sidebar)
        text_draw(draw, (1426, 45), 'Helvetica_Neue_LT_Std_75_Bold.otf', 58, get_json(json, 'artist.group', ''),
                  get_json(json, 'appearance.text_color', '#000000'), pos=2)

    sidebar = sidebar.rotate(270, expand=True)
    backside = paste_correctly(backside, (865, 98), sidebar)




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
            "background_color": "#000",
            "text_color": "#00FF00",
        },
        "identifiers": {
            "number": 100,
            "alphabet": None,
            "serial": 1
        },
        "text_area": {
            "class": "First",
            "season": "Atom01",
            "qr_code": "https://objektify.xyz"
        }
    }

    generate_back(data).show()