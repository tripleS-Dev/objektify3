import gradio as gr
from config import dev_option

def hidden():
    with gr.Group('hidden', visible=False):
        input_image_raw = gr.Image(type='pil', image_mode='RGBA', visible=False)
        true = gr.Checkbox(value=True, visible=False)
        false = gr.Checkbox(value=False, visible=False)

        front_raw = gr.File(type='filepath', visible=False)
        back_raw = gr.File(type='filepath', visible=False)
        combined_raw = gr.File(type='filepath', visible=False)

        raws = [front_raw, back_raw, combined_raw]

        temp_id = gr.Textbox(visible=False)
        cache_id = gr.Textbox(visible=False)

    return input_image_raw, true, false, front_raw, back_raw, combined_raw, raws, temp_id, cache_id