import gradio as gr
from generate.front import resize_round, make_json
from utils import on_load, season_load, paste_correctly, class_load



def front(input_image_raw=None, input_image=None, front_components=None, others=None, advanced_components=None, true=None, false=None, demo=None, difficult=None):
    artist, season, classes, member, numbering_state, number, alphabet, serial, qr_code = front_components
    download_btn, share_btn, go_advanced, numbering, qrcoding = others


    go_advanced.click(fn=lambda: gr.Tabs(selected=1), inputs=None, outputs=difficult)

    all_components = [input_image_raw, artist, season, classes, member, numbering_state, number, alphabet, serial, qr_code]

    if not any(component == '' for component in [input_image_raw, artist]):
        for component in all_components:
            if not component == artist:
                component.input(fn=make_json, inputs=all_components,
                                outputs=[input_image, download_btn] + advanced_components)

            else:
                component.input(fn=lambda x, y: make_json(x, y) + [False], inputs=[input_image_raw, artist],
                                outputs=[input_image, download_btn] + advanced_components + [numbering_state])

    input_image.upload(fn=resize_round, inputs=[input_image] + all_components,
                       outputs=[input_image, input_image_raw, share_btn]+ advanced_components)

    numbering.expand(fn=lambda a, b, c, d, e, f, g, h, i, j: make_json(a, b, c, d, e, f, g, h, i, j) + [True],
                     inputs=all_components[:5] + [true] + all_components[6:],
                     outputs=[input_image, download_btn] + advanced_components + [numbering_state])
    numbering.collapse(fn=lambda a, b, c, d, e, f, g, h, i, j: make_json(a, b, c, d, e, f, g, h, i, j) + [False],
                       inputs=all_components[:5] + [false] + all_components[6:],
                       outputs=[input_image, download_btn] + advanced_components + [numbering_state])

    artist.change(fn=season_load, inputs=artist,
                  outputs=[season, classes, member, numbering, number, alphabet, serial, qrcoding, qr_code])
    season.change(fn=class_load, inputs=[artist, season, classes], outputs=[classes])
    classes.input(fn=lambda: (gr.Dropdown(visible=True)), outputs=[member])
    member.input(fn=lambda: (gr.Group(visible=True), '100', 'Z', '1', gr.Group(visible=True)),
                 outputs=[numbering, number, alphabet, serial, qrcoding])

    demo.load(fn=on_load, outputs=artist)