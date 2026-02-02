import gradio as gr

def member_load(classes):
    if classes == "Unit":
        return gr.Dropdown(visible=False, value=''), gr.CheckboxGroup(visible=True), gr.Group(visible=False)

    elif classes == "Double":
        return gr.Dropdown(visible=True), gr.CheckboxGroup(visible=False, value=None), gr.Group(visible=True)

    else:
        return gr.Dropdown(visible=True), gr.CheckboxGroup(visible=False, value=None), gr.Group(visible=False)
