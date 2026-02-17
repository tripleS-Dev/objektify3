import gradio as gr
from html_elements import ads
import config

def simple_plus():
    with gr.Tab('Simple+', id=1) as simple_plus:
        with gr.Group('hidden', visible=False):
            pass
        with gr.Column():
            artist = gr.Textbox(placeholder=config.simple_plus_placeholder['artist'], label='Artist', value=None, interactive=True, max_lines=1)
            season = gr.Textbox(placeholder=config.simple_plus_placeholder['season'], label='Season', value=None, interactive=True, visible=True, max_lines=1)
            classes = gr.Textbox(placeholder=config.simple_plus_placeholder['class'], label='Class', value=None, interactive=True, visible=True, max_lines=1)

            with gr.Group(visible=True) as colors:
                with gr.Row():
                    color_mode_choices = ['Static', 'AI Colorful']
                    ai_color_choices = ['Red', 'Pink', 'Purple', 'Blue', 'Cyan', 'Green', 'Yellow', 'Orange']
                    ai_color_shape_choices = ['Gradient', 'Wave']

                    color_mode = gr.Radio(choices=color_mode_choices, label='Color Type', value=color_mode_choices[0])

                with gr.Group(visible=False) as ai_options:
                    with gr.Row(equal_height=True):
                        with gr.Column(scale=50):
                            ai_color = gr.Checkboxgroup(interactive=True, label='AI Colorful', info='(Multi-select)', visible=True, choices=ai_color_choices)
                            ai_color_shape = gr.Radio(interactive=True, label='AI Shape', visible=True, choices=ai_color_shape_choices, value=ai_color_shape_choices[0])
                            ai_generate = gr.Button(interactive=True, value='Generate', variant='primary')

                        with gr.Column(scale=1):
                            ai_preview = gr.Image(interactive=False, visible=True, sources=None, label='Preview', elem_classes='preview-image', height=220)


                    with gr.Accordion('AI Others', visible=True, open=False):
                        with gr.Row():

                            ai_color_seed = gr.Textbox(label='AI Seed', info='use the same seed to recreate the exact same pattern', interactive=True, visible=True, value='0')
                            ai_color_seed_type = gr.Radio(label='After generating', choices=["New random seed", "Keep current seed"], value="New random seed", interactive=True, visible=True)

                with gr.Row(equal_height=True):
                    background_color = gr.ColorPicker(label='Background Color', interactive=True, visible=True, value='#353eaf', min_width = 300)
                    text_color = gr.ColorPicker(label='Text Color', interactive=True, visible=True, value='#000000', min_width = 300)

            member = gr.Textbox(placeholder=config.simple_plus_placeholder['member'], label='Member', value=None, interactive=True, visible=False, max_lines=1)

            with gr.Accordion(visible=True, open=False, label='Numbering') as numbering:
                with gr.Row():
                    number = gr.Textbox(label='Number', value='', interactive=True, max_lines=1)
                    alphabet = gr.Textbox(label='Alphabet', value='', interactive=True, max_lines=1)
                    serial = gr.Textbox(label='Serial', value='', interactive=True, max_lines=1)

            with gr.Accordion(visible=True, open=False, label='QR code') as qrcoding:
                with gr.Row():
                    qr_code = gr.Textbox(label='QR code', value='https://objektify.xyz/', interactive=True, visible=True, max_lines=1)


            gr.HTML(value=ads, visible=True)


    all_components = [artist, season, classes, colors, color_mode, background_color, ai_options, ai_color, ai_color_shape, ai_color_seed, ai_color_seed_type, ai_generate, ai_preview, text_color, member, numbering, number, alphabet, serial, qrcoding, qr_code]


    return all_components