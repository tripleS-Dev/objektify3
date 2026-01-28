import gradio as gr
from components import front, advanced, download_share_sidebar, hidden

from html_elements import css, theme, animation, footer, no_zoom_head
import events
import argparse

with gr.Blocks() as demo:

    input_image_raw, true, false, front_raw, back_raw, combined_raw, raws, temp_id, cache_id = hidden()

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


    events.front(temp_id, cache_id, input_image_raw, input_image, front_components, others, advanced_components, true, false, demo, difficult, download_share_buttons, raws, download_bar)
    #events.advanced(input_image_raw, input_image, advanced_components, true, false, demo, difficult)


# 1. 인자 파서를 설정합니다.
parser = argparse.ArgumentParser(description="Gradio 앱 실행 스크립트")
parser.add_argument(
    "--port",
    type=int,
    default=800,
    help="서버를 실행할 포트 번호 (기본값: 800)"
)

# 2. 인자를 파싱합니다.
args = parser.parse_args()
port = args.port

print(f"http://localhost:{port}")
demo.launch(server_name='0.0.0.0', ssr_mode=False, css=css, theme=theme, js=animation, server_port=port, head=no_zoom_head)
