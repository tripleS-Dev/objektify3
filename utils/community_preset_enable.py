import gradio as gr

from utils import list_artist_folders


def community_preset_enable(check_box):
    if check_box:
        return gr.Dropdown(visible=True, choices=list_artist_folders(False))
    else:
        return gr.Dropdown(visible=False, value='')

