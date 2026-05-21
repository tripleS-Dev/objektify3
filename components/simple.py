import gradio as gr
from html_elements import ads
from utils import list_artist_folders, community_preset_enable


def simple():
    with gr.Tab('Simple', id=0) as simple_tab:


        with gr.Group(visible=False):
            numbering_state = gr.Checkbox(value=False)

        with gr.Column():
            artist = gr.Radio(label='Artist', choices=None, interactive=True)
            season = gr.Radio(label='Season', choices=None, interactive=True, visible=False)
            classes = gr.Radio(label='Class', choices=None, interactive=True, visible=True)

            with gr.Group(visible=False) as colors:
                with gr.Row(equal_height=True):
                    background_color = gr.ColorPicker(label='Background Color', interactive=True, visible=True, value='#E61E2B', min_width = 260)
                    text_color = gr.ColorPicker(label='Text Color', interactive=True, visible=True, value='#000000', min_width = 260)

            member = gr.Dropdown(label='Member', choices=None, interactive=True, visible=True, allow_custom_value=True)
            unit = gr.CheckboxGroup(label='Members', choices=None, interactive=True, visible=True, type='value')

            with gr.Accordion(visible=False, open=False, label='Numbering (expand to enable)') as numbering:
                with gr.Row():
                    number = gr.Textbox(label='Number', value='', interactive=True, min_width = 1)
                    alphabet = gr.Textbox(label='Alphabet', value='', interactive=True, min_width = 1)
                    serial = gr.Textbox(label='Serial', value='', interactive=True, min_width = 1)

            with gr.Accordion(visible=False, open=False, label='QR code') as qrcoding:
                with gr.Row():
                    qr_code = gr.Textbox(label='QR code', value='https://objektify.xyz/', interactive=True, visible=True)

            with gr.Row():
                download_btn = gr.DownloadButton(label='Download', variant="primary", visible=False)
                share_btn = gr.DownloadButton(label='Share', variant="primary", visible=False)
                go_advanced = gr.Button(value='Edit More', variant="primary", visible=False)

                go_download_share = gr.Button(value='Download/Share', variant="primary", visible=True)


            with gr.Group():
                enable_community_preset = gr.Checkbox(label='Enable community presets')
                community_preset = gr.Dropdown(allow_custom_value=False, choices=None, interactive=True, visible=True, multiselect=True, label='Presets to enable')
                enable_community_preset.input(fn=community_preset_enable, inputs=enable_community_preset, outputs=community_preset)
                community_preset.input(fn=lambda x: gr.Radio(choices=list_artist_folders(True)+x), inputs=community_preset, outputs=artist)

            gr.HTML(value=ads, visible=True)


    all_components = [artist, season, classes, colors, background_color, text_color, member, unit, numbering_state, number, alphabet, serial, qr_code]

    others = [download_btn, share_btn, go_advanced, numbering, qrcoding, go_download_share, simple_tab, community_preset]

    return all_components, others