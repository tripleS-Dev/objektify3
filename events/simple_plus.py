import gradio as gr
from generate.front import resize_round, make_json
from utils import on_load, season_load, paste_correctly, class_load, member_load, color_mode_input
from generate.simple_plus import make_ai_gradient
from html_elements import toggle_sidebar


def simple_plus(temp_id, cache_id, input_image_raw, simple_plus_components):
    artist, season, classes, colors, color_mode, background_color, ai_options, ai_color, ai_color_shape, ai_color_seed, ai_color_seed_type, ai_generate, ai_preview, ai_sidebar, ai_back, text_color, member, numbering, number, alphabet, serial, qrcoding, qr_code = simple_plus_components

    #artist.input(fn=lambda : gr.Textbox(visible=True), outputs=season)
    #season.input(fn=lambda : gr.Textbox(visible=True), outputs=classes)
    #classes.input(fn=lambda : (gr.Group(visible=True), gr.Textbox(visible=True)), outputs=[colors, member])
    #member.input(fn=lambda : (gr.Accordion(visible=True), gr.Accordion(visible=True)), outputs=[numbering, qrcoding])


    color_mode.input(fn=color_mode_input, inputs=color_mode, outputs=[ai_options, background_color])
    ai_generate.click(fn=make_ai_gradient, inputs=[ai_color, ai_color_shape, ai_color_seed], outputs=[ai_preview, ai_sidebar, ai_back])



    generate_components = [artist, season, classes, background_color, text_color, number, alphabet, serial, qr_code]
    input_components = [artist, season, classes, colors, color_mode, background_color, ai_options, ai_color, ai_color_shape, ai_color_seed, ai_color_seed_type, ai_generate, ai_preview, ai_sidebar, ai_back, text_color, member, numbering, number, alphabet, serial, qrcoding, qr_code]

    for component in generate_components:
        if component in [background_color, text_color]:
            component.input(fn=lambda : gr.Info('blur'))
        else:
            component.blur(fn=lambda : gr.Info('blur'))
