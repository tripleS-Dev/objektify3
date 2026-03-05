import gradio as gr

from generate.simple_plus import make_ai_gradient
from utils import color_mode_input


def color_components(boolen):
    with gr.Group(visible=True) as colors:
        with gr.Row():
            color_mode_choices = ['Static', 'AI Colorful']
            ai_color_choices = ['Red', 'Pink', 'Purple', 'Blue', 'Cyan', 'Green', 'Yellow', 'Orange']
            ai_color_shape_choices = ['Gradient', 'Wave']

            color_mode = gr.Radio(choices=color_mode_choices, label='Color Type',
                                  value=color_mode_choices[0], visible=boolen, interactive=True)


        with gr.Group(visible=False) as ai_options:
            with gr.Row(equal_height=True):
                with gr.Column(scale=50):
                    ai_color = gr.Checkboxgroup(interactive=True, label='AI Colorful',
                                                info='(Multi-select)', visible=True,
                                                choices=ai_color_choices)
                    ai_color_shape = gr.Radio(interactive=True, label='AI Shape', visible=True,
                                              choices=ai_color_shape_choices,
                                              value=ai_color_shape_choices[0])
                    ai_generate = gr.Button(interactive=True, value='Generate', variant='primary')

                with gr.Column(scale=1):
                    ai_preview = gr.Image(interactive=False, visible=True, sources=None,
                                          label='Preview', elem_classes='preview-image', height=220,
                                          type='pil', buttons=[])
                    ai_sidebar = gr.Image(interactive=False, visible=False, type='pil')
                    ai_back = gr.Image(interactive=False, visible=False, type='pil')

            with gr.Accordion('AI Others', visible=True, open=False):
                with gr.Row():
                    ai_color_seed = gr.Textbox(label='AI Seed',
                                               info='use the same seed to recreate the exact same pattern',
                                               interactive=True, visible=True, value='0')
                    ai_color_seed_type = gr.Radio(label='After generating',
                                                  choices=["New random seed", "Keep current seed"],
                                                  value="New random seed", interactive=True,
                                                  visible=True)

        with gr.Row(equal_height=True):
            background_color = gr.ColorPicker(label='Background Color', interactive=True, visible=True,
                                              value='#353eaf', min_width=260)  # width 너무 작으면 모바일에서 깨짐
            text_color = gr.ColorPicker(label='Text Color', interactive=True, visible=True,
                                        value='#000000', min_width=260)

            color_mode.input(fn=color_mode_input, inputs=color_mode, outputs=[ai_options, background_color])
            ai_generate.click(fn=make_ai_gradient, inputs=[ai_color, ai_color_shape, ai_color_seed],
                              outputs=[ai_preview, ai_sidebar, ai_back])