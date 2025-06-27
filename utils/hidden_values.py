import gradio as gr

def hidden_values():
    with gr.Group():
        all_artists = gr.Textbox()

    return all_artists