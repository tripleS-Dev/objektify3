import gradio as gr

def class_tab_list():
    colors = []
    tabs = []
    
    with gr.Tab(label='', id=0) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=1) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=2) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=3) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=4) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=5) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=6) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=7) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=8) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)

    with gr.Tab(label='', id=9) as tab0:
        with gr.Row(equal_height=True):
            colors.append(color())
            tabs.append(tab0)
    return tabs, colors


def color():
    bc = gr.ColorPicker(label='Background Color', interactive=True, visible=True, value='#353eaf', min_width=260)  # width 너무 작으면 모바일에서 깨짐
    tc = gr.ColorPicker(label='Text Color', interactive=True, visible=True, value='#000000', min_width=260)
    return (bc, tc)