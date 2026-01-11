import gradio as gr
from config import dev_option

def hidden():
    with gr.Group('hidden', visible=dev_option):
        input_image_raw = gr.Image(type='pil', image_mode='RGBA')
        true = gr.Checkbox(value=True)
        false = gr.Checkbox(value=False)

        front_raw = gr.File(type='filepath')
        back_raw = gr.File(type='filepath')
        combined_raw = gr.File(type='filepath')

        raws = [front_raw, back_raw, combined_raw]

    return input_image_raw, true, false, front_raw, back_raw, combined_raw, raws