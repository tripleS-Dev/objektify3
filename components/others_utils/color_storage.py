import gradio as gr

def color_storage(default='#FFFFFF'):
    colors = []

    for i in range(20):
        colors.append(gr.ColorPicker(value=default, visible=True))