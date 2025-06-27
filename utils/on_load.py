from utils import list_artist_folders, hidden_values
import gradio as gr

def on_load():
    all_artists = list_artist_folders(True)
    return gr.Dropdown(label='Artist', choices=all_artists)