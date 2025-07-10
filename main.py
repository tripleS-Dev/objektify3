import gradio as gr
from components import front, sidebar

from html_elements import css, theme, animation


with gr.Blocks(css=css, theme=theme, js=animation) as demo:
    #sidebar(False)
    with gr.Group('hidden', visible=False):
        input_image_raw = gr.Image(type='pil', image_mode='RGBA')

    with gr.Row():
        with gr.Row(elem_classes='sticky-image'):
            input_image = gr.Gallery(type='filepath', interactive=True, show_download_button=True, show_fullscreen_button=True, format='png', show_label=False, elem_classes='sticky-image', preview=True, file_types=['.png', '.jpg', '.jpeg', '.webp'], object_fit='contain', height='100%')

        front(demo, input_image_raw, input_image)


demo.launch(server_name='0.0.0.0')
