import gradio as gr
from components import simple, advanced, download_share_sidebar, hidden, simple_plus, others_tab

from html_elements import css, theme, animation, footer, no_zoom_head
import events
import argparse
from utils import on_load
import generate.modhaus.classes


with gr.Blocks(title='Objektify') as demo:

    true, false, front_raw, back_raw, combined_raw, raws, temp_id, cache_id, first_act = hidden()

    with gr.Row():
        with gr.Row(elem_classes='sticky-image') as image_box:
            input_image = gr.Gallery(type='filepath', interactive=True, format='png', show_label=False, elem_classes='sticky-image', preview=True, file_types=['.png', '.jpg', '.jpeg', '.webp'], object_fit='contain', height='100%', buttons=['download','fullscreen'], visible=True)
            objekt = gr.State()
        with gr.Column():
            with gr.Tabs() as tabs:
                simple_components, others = simple()
                simple_plus_components = simple_plus()
                others_tab(image_box)
                #advanced_components = advanced()
            gr.Markdown(value="\n\n\n\n")
            gr.Markdown(value="\n\n\n\n")

            gr.Markdown(value=footer)


    download_bar, download_share_buttons = download_share_sidebar(raws, others[5])


    events.simple(objekt, temp_id, cache_id, input_image, simple_components, others, true, false, demo, tabs, download_share_buttons, raws, download_bar, first_act, image_box, simple_plus_components)
    events.simple_plus(objekt, temp_id, cache_id, input_image, simple_plus_components, download_share_buttons, raws)

    #demo.load(fn=on_load, outputs=simple_components[0])
    demo.load(fn=lambda : gr.Info('New features are here:\nSimple Plus (Full Edit) and Preset Maker are now available!', duration=5))



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

if __name__ == "__main__":
    print(f"http://localhost:{port}")
    demo.launch(server_name='0.0.0.0', ssr_mode=False, css=css, theme=theme, js=animation, server_port=port, head=no_zoom_head, pwa=True)
