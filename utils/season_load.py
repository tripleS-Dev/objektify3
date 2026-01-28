import os
import json
import gradio as gr
from PIL import Image


def season_load(artist_name):
    config_path = os.path.join('./artists', artist_name, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    seasons = config.get('seasons', {}).keys()

    members = config.get('members', []).keys()

    abbrs = [
        (info.get("abbr") or name)
        for name, info in config.get("members", {}).items()
    ]

    return gr.Radio(label='Season', choices=seasons, interactive=True, visible=True, value=None), gr.Radio(label='Class', choices=None, interactive=True, visible=False, value=None), gr.Dropdown(label='Member', choices=members, interactive=True, visible=False, value=''), gr.CheckboxGroup(label='Members', choices=abbrs, interactive=True, visible=False, value=None), gr.Accordion(open=False, visible=False), '100', 'Z', '1', gr.Accordion(open=False, visible=False), gr.Textbox(value='https://objektify.xyz/', visible=True)


def class_load(artist_name, season, classes):
    if not season:
        return gr.Radio(label='Class', choices=None, interactive=True, visible=False, value=None)

    config_path = os.path.join('./artists/', artist_name, 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)

    data = list(config.get('seasons', {}).get(season, None).keys())
    del data[data.index('display')]



    return gr.Radio(label='Class', choices=data, interactive=True, visible=True if data else False, value=classes if classes in data else None)