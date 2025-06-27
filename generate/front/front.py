from PIL import Image, ImageOps, ImageDraw
from pathlib import Path

from utils import color_change, paste_correctly, text_draw, get_json

BASE_DIR = str(Path(__file__).resolve().parent) + '/resources/'




def generate_front(image, json, side_logo: Image.Image = None, side_bar_img: Image.Image = None) -> Image.Image:
    if not image:
        image = Image.open(BASE_DIR+'test.png')



    if side_bar_img:
        sidebar = side_bar_img
    else:
        sidebar = Image.open(BASE_DIR+'sidebar.png')
        sidebar = color_change(sidebar, get_json(json, 'appearance.background_color', '#FFFFFF'))


    draw = ImageDraw.Draw(sidebar)

    text_draw(draw, (49, 51), 'Helvetica_Neue_LT_Std_75_Bold.otf', 56, get_json(json, 'artist.name', ''), get_json(json, 'appearance.text_color', '#000000'))

    if side_logo:
        side_logo = color_change(side_logo, get_json(json, 'appearance.text_color', '#000000'))

        sidebar = paste_correctly(sidebar, (1478-55-side_logo.size[0], 37), side_logo)
        draw = ImageDraw.Draw(sidebar)

    else:
        text_draw(draw, (1426, 45), 'Helvetica_Neue_LT_Std_75_Bold.otf', 58, get_json(json, 'artist.group', ''), get_json(json, 'appearance.text_color', '#000000'), pos=2)


    if get_json(json, 'identifiers.number', None) and get_json(json, 'identifiers.serial', None):
        text_draw(draw, (662+4, 31), 'Inter-Bold-5.ttf', 54, str(get_json(json, 'identifiers.number', ''))+str(get_json(json, 'identifiers.alphabet', '')), get_json(json, 'appearance.text_color', '#000000'), pos=2)
        text_draw(draw, (682, 44), 'MatrixSSK_custom.ttf', 60, '#'+str(get_json(json, 'identifiers.serial', '')).zfill(6), get_json(json, 'appearance.text_color', '#000000'), pos=0)

    if get_json(json, 'identifiers.number', None) and not get_json(json, 'identifiers.serial', None):
        text_draw(draw, (sidebar.size[0]/2, sidebar.size[1]/2 - 14), 'Inter-Bold-5.ttf', 56, str(get_json(json, 'identifiers.number', ''))+str(get_json(json, 'identifiers.alphabet', '')), get_json(json, 'appearance.text_color', '#000000'), pos=1)


    sidebar = sidebar.rotate(270, expand=True)

    image = paste_correctly(image, (965, 98), sidebar)

    return image

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
    img = Image.new('RGBA', (1083, 1673), (255, 255, 255))

    #generate_front(img, data).save('dsd.png')
    generate_front(img, data).show()