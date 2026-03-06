from utils import rgba_to_hex
import gradio as gr

def color_change(seasons_select, class_select, bc, tc, color_json):
    print(color_json)

    if not class_select:
        gr.Info('You should select Class Fist')
        return color_json


    if not color_json['seasons'].get(seasons_select):
        color_json['seasons'][seasons_select] = {}


    color_json['seasons'][seasons_select][class_select] = [rgba_to_hex(bc), rgba_to_hex(tc)]

    return color_json
