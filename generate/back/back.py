from PIL import Image, ImageDraw
from pathlib import Path

from utils import color_change, get_json, paste_correctly, text_draw, qr_image

BASE_DIR = str(Path(__file__).resolve().parent) + '/resources/'

def generate_back(json, back_img=None, side_logo=None, top_logo_img=None, sign_img=None, sign_position=None, qr_logo_img=None) -> Image.Image:

    backside, layout, inside = open_images()


    if back_img:
        inside = back_img
    else:
        inside = color_change(inside, get_json(json, 'appearance.background_color', '#000000'))


    layout = color_change(layout, get_json(json, 'appearance.text_color', '#000000'))


    backside = paste_correctly(backside, (0,0), inside)

    backside = paste_correctly(backside, (0,0), layout)


    draw = ImageDraw.Draw(backside)


    text_draw(draw, (55, 471), 'Helvetica_Neue_LT_Std_65_Medium-4.otf', 126, get_json(json, 'artist.name', ''), get_json(json, 'appearance.text_color', '#000000'))
    text_draw(draw, (55, 471+216), 'Helvetica_Neue_LT_Std_65_Medium-4.otf', 126, get_json(json, 'text_area.class', ''), get_json(json, 'appearance.text_color', '#000000'))

    season_raw = get_json(json, 'text_area.season', '')
    if '/' in season_raw:
        season = get_json(json, f'text_area.season', '').split('/')[0]
        x, *_ = text_draw(draw, (55, 471 + 216 + 216+8), 'Helvetica_Neue_LT_Std_65_Medium-4.otf', 126, season, get_json(json, 'appearance.text_color', '#000000'))

        season_outline = get_json(json, f'text_area.season', '').split('/')[1]
        text_draw(draw, (55+x+4, 471 + 216 + 216 + 8), 'Helvetica_Neue_LT_Std_65_Medium-4-outline.otf', 126-5, season_outline, get_json(json, 'appearance.text_color', '#000000'))
    else:
        season_outline = ''
        text_draw(draw, (55, 471 + 216 + 216), 'Helvetica_Neue_LT_Std_65_Medium-4.otf', 126, season_raw, get_json(json, 'appearance.text_color', '#000000'))

    if not get_json(json, 'text_area.qr_caption', '') == '':
        text_draw(draw, (670, 1348), 'Inter-SemiBold.ttf', 32, get_json(json, 'text_area.qr_caption', None), get_json(json, 'appearance.text_color', '#000000'), pos=1)


    sidebar = Image.open(BASE_DIR + 'sidebar.png')
    draw_sidebar = ImageDraw.Draw(sidebar)

    text_draw(draw_sidebar, (49, 51), 'Helvetica_Neue_LT_Std_75_Bold.otf', 56, get_json(json, 'artist.name', ''), get_json(json, 'appearance.text_color', '#000000'))


    if top_logo_img:
        top_logo = color_change(top_logo_img, get_json(json, 'appearance.text_color', '#000000'))
        backside = paste_correctly(backside, (57, 151), top_logo)


    if sign_img:
        sign_img = color_change(sign_img, get_json(json, 'appearance.text_color', '#000000'))
        backside = paste_correctly(backside, sign_position if sign_position else (59, 1020), sign_img)




    if side_logo:
        side_logo = color_change(side_logo, get_json(json, 'appearance.text_color', '#000000'))
        sidebar = paste_correctly(sidebar, (1478 - 55 - side_logo.size[0], 37), side_logo)
        draw_sidebar = ImageDraw.Draw(sidebar)

    else:
        text_draw(draw_sidebar, (1426, 45), 'Helvetica_Neue_LT_Std_75_Bold.otf', 58, get_json(json, 'artist.group', ''),  get_json(json, 'appearance.text_color', '#000000'), pos=2)


    if get_json(json, 'identifiers.number', None) and get_json(json, 'identifiers.serial', None):

        text_draw(draw_sidebar, (662+4, 31), 'Inter-Bold-5.ttf', 54, str(get_json(json, 'identifiers.number', ''))+str(get_json(json, 'identifiers.alphabet', '')), get_json(json, 'appearance.text_color', '#000000'), pos=2)
        text_draw(draw_sidebar, (682, 44), 'MatrixSSK_custom.ttf', 60, '#'+str(get_json(json, 'identifiers.serial', '')).zfill(6), get_json(json, 'appearance.text_color', '#000000'), pos=0)

    if get_json(json, 'identifiers.number', None) and not get_json(json, 'identifiers.serial', None):
        text_draw(draw_sidebar, (sidebar.size[0]/2, sidebar.size[1]/2 - 14), 'Inter-Bold-5.ttf', 56, str(get_json(json, 'identifiers.number', ''))+str(get_json(json, 'identifiers.alphabet', '')), get_json(json, 'appearance.text_color', '#000000'), pos=1)




    sidebar = sidebar.rotate(270, expand=True)
    backside = paste_correctly(backside, (865, 98), sidebar)

    if get_json(json, 'text_area.qr_code', None):
        qr_code = qr_image(get_json(json, 'text_area.qr_code', None), qr_logo_img)
        backside = paste_correctly(backside, (514, 1020), qr_code)





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