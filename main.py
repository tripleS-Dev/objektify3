import gradio as gr
from components import front, sidebar

from html_elements import css, theme, animation


with gr.Blocks(css=css, theme=theme, js=animation) as demo:
    sidebar(False)

    front(demo)


demo.launch(server_name='0.0.0.0')
