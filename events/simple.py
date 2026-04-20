import gradio as gr
from generate.front import resize_round, make_json
from utils import season_load, paste_correctly, class_load, member_load
from html_elements import toggle_sidebar
from utils import on_load


def simple(temp_id, cache_id=None, input_image_raw=None, input_image=None, simple_components=None, others=None, true=None, false=None, demo=None, tabs=None, download_share_buttons=None, raws = None, download_bar = None, first_act = None, image_box = None):
    artist, season, classes, colors, background_color, text_color, member, unit, numbering_state, number, alphabet, serial, qr_code = simple_components
    download_btn, share_btn, go_advanced, numbering, qrcoding, go_download_share, simple_tab = others
    download_front, download_back, download_combine, share_front, share_back, share_combined = download_share_buttons

    front_raw, back_raw, combined_raw = raws

    go_advanced.click(fn=lambda: gr.Tabs(selected=1), inputs=None, outputs=tabs)
    #go_download_share.click(fn=lambda : [gr.Sidebar(open=True), gr.Button(variant="secondary")], outputs=[download_bar, go_download_share])

    go_download_share.click(fn=None, inputs=[], outputs=[], js=toggle_sidebar)

    all_components = [temp_id, cache_id, input_image_raw, artist, season, classes, background_color, text_color, member, unit, numbering_state, number, alphabet, serial, qr_code]

    if not any(component == '' for component in [input_image_raw, artist]):
        for component in all_components:
            if component == artist:
                component.input(fn=lambda x, y, z, r: make_json(x, y, z, r) + [False], inputs=[temp_id, cache_id, input_image_raw, artist],
                                outputs=[cache_id, input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw] + [numbering_state])
            elif component in [member, number, alphabet, serial, qr_code]:
                component.blur(fn=make_json, inputs=all_components,
                                outputs=[cache_id, input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw])

            elif component in [background_color, text_color]: # pip install https://gradio-pypi-previews.s3.amazonaws.com/f46c77b7509f1266e09c11beff24a79650e2d4fd/gradio-6.5.1-py3-none-any.whl
                # https://github.com/gradio-app/gradio/issues/12896
                component.blur(fn=make_json, inputs=all_components,   #I want to '.blur' but it has bug https://github.com/gradio-app/gradio/issues/12854
                                outputs=[cache_id, input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw])

            elif component == numbering_state:
                component.change(fn=make_json, inputs=all_components,
                                outputs=[cache_id, input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw])

            elif component == unit:
                component.input(fn=make_json, inputs=all_components,
                                outputs=[cache_id, input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw])

            elif component in [temp_id, cache_id]:
                pass

            else:
                component.input(fn=make_json, inputs=all_components,
                                outputs=[cache_id, input_image, download_front, download_back, download_combine, front_raw, back_raw, combined_raw])

    input_image.upload(fn=resize_round, inputs=[input_image] + all_components[1:],
                       outputs=[temp_id, cache_id, input_image, input_image_raw, download_front, download_back, download_combine, front_raw, back_raw, combined_raw])


    numbering.expand(fn=lambda : gr.Checkbox(value=True), outputs=numbering_state)
    numbering.collapse(fn=lambda : gr.Checkbox(value=False), outputs=numbering_state)

    artist.change(fn=season_load, inputs=artist,
                  outputs=[season, classes, member, unit, numbering, number, alphabet, serial, qrcoding, qr_code])
    season.change(fn=class_load, inputs=[artist, season, classes], outputs=classes)
    classes.input(fn=member_load, inputs=classes, outputs=[member, unit, colors])
    member.input(fn=lambda: (gr.Group(visible=True), gr.Group(visible=True)),
                 outputs=[numbering, qrcoding])
    unit.input(fn=lambda: (gr.Group(visible=True), gr.Group(visible=True)),
                 outputs=[numbering, qrcoding])



    #https://github.com/gradio-app/gradio/issues/13302
    simple_tab.select(fn=lambda x: (gr.Row(visible=True), on_load(), gr.Radio(visible=False), gr.Dropdown(visible=False), gr.Radio(visible=False)) if not x else (gr.Row(visible=True), on_load(), gr.Radio(), gr.Dropdown, gr.Radio), inputs=[first_act], outputs=[image_box, artist, classes, member, unit])


    #input_image.change(fn=lambda x: print(x), inputs=input_image)