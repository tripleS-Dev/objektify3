import gradio as gr


def color_mode_input(mode: str):

    if mode == 'Static':
        visible = False
    elif mode == 'AI Colorful':
        visible = True
    else:
        visible = False


    return gr.Accordion(visible=visible), gr.ColorPicker(visible=not visible)
