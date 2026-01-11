import gradio as gr
from generate.front import resize_round, make_json
from utils import on_load, season_load, paste_correctly, class_load
from html_elements import toggle_sidebar


def front(input_image_raw=None, input_image=None, front_components=None, others=None, advanced_components=None, true=None, false=None, demo=None, difficult=None, download_share_buttons=None, raws = None, download_bar = None):
    artist, season, classes, member, numbering_state, number, alphabet, serial, qr_code = front_components
    download_btn, share_btn, go_advanced, numbering, qrcoding, go_download_share = others
    download_front, download_back, download_combine, share_front, share_back, share_combined = download_share_buttons

    front_raw, back_raw, combined_raw = raws

    go_advanced.click(fn=lambda: gr.Tabs(selected=1), inputs=None, outputs=difficult)
    #go_download_share.click(fn=lambda : [gr.Sidebar(open=True), gr.Button(variant="secondary")], outputs=[download_bar, go_download_share])

    go_download_share.click(fn=None, inputs=[], outputs=[], js=toggle_sidebar)

    all_components = [input_image_raw, artist, season, classes, member, numbering_state, number, alphabet, serial, qr_code]

    if not any(component == '' for component in [input_image_raw, artist]):
        for component in all_components:
            if component == artist:
                component.input(fn=lambda x, y: make_json(x, y) + [False], inputs=[input_image_raw, artist],
                                outputs=[input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw] + advanced_components + [numbering_state])
            elif component == member:
                component.blur(fn=make_json, inputs=all_components,
                                outputs=[input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw] + advanced_components)
            else:
                component.input(fn=make_json, inputs=all_components,
                                outputs=[input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw] + advanced_components)

    input_image.upload(fn=resize_round, inputs=[input_image] + all_components,
                       outputs=[input_image, input_image_raw, download_front, download_back, download_combine, front_raw, back_raw, combined_raw]+ advanced_components)

    numbering.expand(fn=lambda a, b, c, d, e, f, g, h, i, j: make_json(a, b, c, d, e, f, g, h, i, j) + [True],
                     inputs=all_components[:5] + [true] + all_components[6:],
                     outputs=[input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw] + advanced_components + [numbering_state])
    numbering.collapse(fn=lambda a, b, c, d, e, f, g, h, i, j: make_json(a, b, c, d, e, f, g, h, i, j) + [False],
                       inputs=all_components[:5] + [false] + all_components[6:],
                       outputs=[input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw] + advanced_components + [numbering_state])

    artist.change(fn=season_load, inputs=artist,
                  outputs=[season, classes, member, numbering, number, alphabet, serial, qrcoding, qr_code])
    season.change(fn=class_load, inputs=[artist, season, classes], outputs=classes)
    classes.input(fn=lambda: gr.Dropdown(visible=True), outputs=member)
    member.input(fn=lambda: (gr.Group(visible=True), '100', 'Z', '1', gr.Group(visible=True)),
                 outputs=[numbering, number, alphabet, serial, qrcoding])

    demo.load(fn=on_load, outputs=artist)



    #input_image.change(fn=lambda x: print(x), inputs=input_image)