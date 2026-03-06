import gradio as gr

from utils import rgba_to_hex


def by_season_init(add_seasons, color_json): # -> seasons_select, class_name, color_json

    if not color_json.get('seasons'):
        color_json['seasons'] = {}


    # color_json에는 있지만 class_names에는 없는 키 삭제
    for key in list(color_json['seasons'].keys()):
        if key not in add_seasons:
            del color_json['seasons'][key]

    for season in add_seasons:
        if not color_json['seasons'].get(season):
            color_json['seasons'][season] = {}


    return gr.Radio(choices=add_seasons, value=add_seasons[0]), gr.Dropdown(choices=None), color_json

def class_name_change(seasons_select, class_names, color_json, bc, tc):

    season_colors = color_json['seasons'][seasons_select]


    # color_json에는 있지만 class_names에는 없는 키 삭제
    for key in list(season_colors.keys()):
        if key not in class_names:
            del season_colors[key]


    if not len(class_names) >= 1:
        return gr.Radio(choices=class_names, value=None), color_json




    # class_names에는 있지만 color_json에는 없는 키 추가
    for class_name in class_names:
        if class_name not in season_colors:
            season_colors[class_name] = [rgba_to_hex(bc), rgba_to_hex(tc)]

    return gr.Radio(choices=class_names, value=class_names[0]), color_json