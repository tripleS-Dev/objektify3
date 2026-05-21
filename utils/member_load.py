import gradio as gr
import os
import json
from utils import get_json


def member_load(artist_name, season, classes):

    config_path = os.path.join('./artists/', artist_name, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    if get_json(config, f'seasons.{season}.{classes}', None):
        if get_json(config, f'seasons.{season}.{classes}', None)[0] == "@choose":
            choose = True
        else:
            choose = False
    else:
        choose = False


    if classes == "Unit":
        return gr.Dropdown(visible=False, value=''), gr.CheckboxGroup(visible=True), gr.Group(visible=False)


    return gr.Dropdown(visible=True), gr.CheckboxGroup(visible=False, value=None), gr.Group(visible=choose)

