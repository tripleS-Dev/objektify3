from utils import get_json
import gradio as gr

def simple2advanced(data, sign=None, sign_position_x=None, sign_position_y=None):
    #advanced_components = [main_color, text_color, name, group_text, class_, season, season_outline, number, alphabet, serial, sign, sign_scale, sign_position, qr_code, qr_logo, qr_caption, sidebar_logo, top_logo, sidebar, back_layout]
    print(data)

    main_color = get_json(data, f'appearance.background_color', '')
    if not main_color.startswith('#'):
        main_color = '#FFFFFF'

    text_color = get_json(data, f'appearance.text_color', '')

    name = get_json(data, f'artist.name', '')
    group_text = get_json(data, f'artist.group', '')

    class_ = get_json(data, f'text_area.class', '')
    season = get_json(data, f'text_area.season', '')
    season_outline = None

    number = get_json(data, f'identifiers.number', '')
    alphabet = get_json(data, f'identifiers.alphabet', '')

    serial = get_json(data, f'identifiers.serial', '')

    sign = sign
    sign_scale = 1
    sign_position_x= sign_position_x


    qr_code = get_json(data, f'text_area.qr_code', '')

    qr_logo, qr_caption, sidebar_logo, top_logo, sidebar, back_layout = None, None, None, None, None, None

    return [gr.ColorPicker(value=main_color), gr.ColorPicker(value=text_color), gr.Textbox(value=name), gr.Textbox(value=group_text), gr.Textbox(value=class_), gr.Textbox(value=season), gr.Textbox(value=season_outline), gr.Textbox(value=number), gr.Textbox(value=alphabet), gr.Textbox(value=serial), sign, sign_scale, gr.Slider(value=sign_position_x), gr.Slider(value=sign_position_y), gr.Textbox(value=qr_code), qr_logo, qr_caption, sidebar_logo, top_logo, sidebar, back_layout]


if __name__ == '__main__':
    data = {
        "artist": {
            "name": "dsd",
            "group": "dsd"
        },
        "appearance": {
            "background_color": "dsd",
            "text_color": "text_color",
        },
        "identifiers": {
            "number": 'number',
            "alphabet": 'alphabet',
            "serial": 'serial'
        },
        "text_area": {
            "class": 'class_',
            "season": 'season',
            "qr_code": 'qr_code'
        }
    }

    a = simple2advanced(data)

    print(a)