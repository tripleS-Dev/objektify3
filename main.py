import gradio as gr
from components import front, advanced, download_share_sidebar, hidden

from html_elements import css, theme, animation, footer, no_zoom_head
import events


with gr.Blocks() as demo:

    input_image_raw, true, false, front_raw, back_raw, combined_raw, raws, temp_id = hidden()

    with gr.Row():
        with gr.Row(elem_classes='sticky-image'):
            input_image = gr.Gallery(type='filepath', interactive=True, format='png', show_label=False, elem_classes='sticky-image', preview=True, file_types=['.png', '.jpg', '.jpeg', '.webp'], object_fit='contain', height='100%', buttons=['download','fullscreen'])

        with gr.Column():
            with gr.Tabs() as difficult:
                front_components, others = front()
                advanced_components = advanced()
            gr.Markdown(value="\n\n\n\n")
            gr.Markdown(value="\n\n\n\n")

            gr.Markdown(value=footer)


    download_bar, download_share_buttons = download_share_sidebar(raws, others[5])


    events.front(temp_id, input_image_raw, input_image, front_components, others, advanced_components, true, false, demo, difficult, download_share_buttons, raws, download_bar)
    #events.advanced(input_image_raw, input_image, advanced_components, true, false, demo, difficult)

print("http://localhost:800")
demo.launch(server_name='0.0.0.0', ssr_mode=False, css=css, theme=theme, js=animation, server_port=800, head=no_zoom_head)
