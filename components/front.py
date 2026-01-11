import gradio as gr
import json

from PIL import Image, ImageOps

from generate.front import resize_round, make_json
from utils import on_load, season_load, paste_correctly, class_load

from config import dev_option


def front():
    with gr.Tab('Simple', id=0) as simple:
        with gr.Group('hidden', visible=dev_option):
            numbering_state = gr.Checkbox(value=False)

        with gr.Column():
            artist = gr.Radio(label='Artist', choices=None, interactive=True)
            season = gr.Radio(label='Season', choices=None, interactive=True, visible=False)
            classes = gr.Radio(label='Class', choices=None, interactive=True, visible=False)
            member = gr.Dropdown(label='Member', choices=None, interactive=True, visible=False, allow_custom_value=True)

            with gr.Accordion(visible=False, open=False, label='Numbering (expand to enable)') as numbering:
                with gr.Row():
                    number = gr.Textbox(label='Number', value='', interactive=True)
                    alphabet = gr.Textbox(label='Alphabet', value='', interactive=True)
                    serial = gr.Textbox(label='Serial', value='', interactive=True)

            with gr.Accordion(visible=False, open=False, label='QR code') as qrcoding:
                with gr.Row():
                    qr_code = gr.Textbox(label='QR code', value='https://objektify.xyz/', interactive=True)

            with gr.Row():
                download_btn = gr.DownloadButton(label='Download', variant="primary", visible=False)
                share_btn = gr.DownloadButton(label='Share', variant="primary", visible=False)
                go_advanced = gr.Button(value='Edit More', variant="primary", visible=False)

                go_download_share = gr.Button(value='Download/Share', variant="primary", visible=True)

    all_components = [artist, season, classes, member, numbering_state, number, alphabet, serial, qr_code]

    others = [download_btn, share_btn, go_advanced, numbering, qrcoding, go_download_share]

    return all_components, others