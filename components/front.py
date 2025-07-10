import gradio as gr
import json

from PIL import Image, ImageOps

from generate.front import resize_round, make_json
from utils import on_load, season_load, paste_correctly, class_load


def front(demo, input_image_raw, input_image):
    with gr.Tab('main') as tab:
        with gr.Group('hidden', visible=False):
            numbering_state = gr.Checkbox(value=False)
            true = gr.Checkbox(value=True)
            false = gr.Checkbox(value=False)



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

                #number.input(fn=lambda x: x if x.isdigit() or x == '' else '100', inputs=number, outputs=number)

            with gr.Group():
                with gr.Column():
                    #btn = gr.Button(value='Make', variant="primary")
                    download_btn = gr.DownloadButton(label='Download', variant="primary")
                    share_btn = gr.DownloadButton(label='Share', variant="primary", visible=False)
                    #gr.CheckboxGroup(choices=['Front','back','sum'], label='')

    all_components = [input_image_raw, artist, season, classes, member, numbering_state, number, alphabet, serial, qr_code]

    if not any(component == '' for component in [input_image_raw, artist]):
        for component in all_components:
            if not component == artist:
                component.input(fn=make_json, inputs=all_components, outputs=[input_image, download_btn])

            else:
                component.input(fn=lambda x, y: make_json(x, y)+[False], inputs=[input_image_raw, artist], outputs=[input_image, download_btn, numbering_state])


    #input_image_raw.change(fn=make_json, inputs=all_components, outputs=[input_image, download_btn])
    input_image.upload(fn=resize_round, inputs=[input_image]+all_components, outputs=[input_image, input_image_raw, share_btn])
    #input_image.preview_open(fn=lambda x: print(x), inputs=input_image)

    numbering.expand(fn=lambda a, b, c, d, e, f, g, h, i, j: make_json(a, b, c, d, e, f, g, h, i, j)+[True], inputs=all_components[:5]+[true]+all_components[6:], outputs=[input_image, download_btn, numbering_state])
    numbering.collapse(fn=lambda a, b, c, d, e, f, g, h, i, j: make_json(a, b, c, d, e, f, g, h, i, j)+[False], inputs=all_components[:5]+[false]+all_components[6:], outputs=[input_image, download_btn, numbering_state])


    #numbering_state.change(fn=make_json, inputs=all_components, outputs=[input_image, download_btn])

    #btn.click(fn=make_json, inputs=all_components, outputs=[input_image, download_btn])



    artist.change(fn=season_load, inputs=artist, outputs=[season, classes, member, numbering, number, alphabet, serial, qrcoding])
    season.change(fn=class_load, inputs=[artist, season, classes],outputs=[classes])
    classes.input(fn=lambda : (gr.Dropdown(visible=True)), outputs=[member])
    member.input(fn=lambda : (gr.Group(visible=True), '100', 'Z', '1', gr.Group(visible=True)), outputs=[numbering, number, alphabet, serial, qrcoding])


    demo.load(fn=on_load, outputs=artist)

    return tab