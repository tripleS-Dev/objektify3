from utils import list_artist_folders, hidden_values
import gradio as gr
from config import ai_enabled


def on_load(enable_custom_preset=False, preset='', value=None):
    if enable_custom_preset and preset:
        all_artists = list_artist_folders(True) + [preset]
    else:
        all_artists = list_artist_folders(True)

    if value:
        return gr.Radio(choices=all_artists, value=value)
    else:
        return gr.Radio(choices=all_artists)