import gradio as gr
from components import front, sidebar, advanced

from html_elements import css, theme, animation
import events

from config import dev_option

with gr.Blocks() as demo:
    #sidebar(False)
    with gr.Group('hidden', visible=dev_option):
        input_image_raw = gr.Image(type='pil', image_mode='RGBA')
        true = gr.Checkbox(value=True)
        false = gr.Checkbox(value=False)


    with gr.Row():
        with gr.Row(elem_classes='sticky-image'):
            input_image = gr.Gallery(type='filepath', interactive=True, format='png', show_label=False, elem_classes='sticky-image', preview=True, file_types=['.png', '.jpg', '.jpeg', '.webp'], object_fit='contain', height='100%')


        with gr.Tabs() as difficult:
            front_components, others = front()
            advanced_components = advanced()


    events.front(input_image_raw, input_image, front_components, others, advanced_components, true, false, demo, difficult)
    events.advanced(input_image_raw, input_image, advanced_components, true, false, demo, difficult)


demo.launch(server_name='0.0.0.0', ssr_mode=True, css=css, theme=theme, js=animation)
