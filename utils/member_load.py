import gradio as gr

def member_load(classes):
    if classes == "Unit":
        return gr.Dropdown(visible=False, value=''), gr.CheckboxGroup(visible=True)
    else:
        return gr.Dropdown(visible=True), gr.CheckboxGroup(visible=False, value=None)
