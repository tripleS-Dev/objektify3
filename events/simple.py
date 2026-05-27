import gradio as gr

from generate.modhaus.simple_callbacks import (
    sync_simple_to_simple_plus,
    update_simple_objekt,
    upload_simple_objekt,
)
from html_elements import toggle_sidebar
from utils import class_load, member_load, on_load, season_load


def simple(
    objekt,
    temp_id,
    cache_id=None,
    input_image=None,
    simple_components=None,
    others=None,
    true=None,
    false=None,
    demo=None,
    tabs=None,
    download_share_buttons=None,
    raws=None,
    download_bar=None,
    first_act=None,
    image_box=None,
    simple_plus_components=None,
):
    artist, season, classes, colors, background_color, text_color, member, unit, numbering_state, number, alphabet, serial, qr_code = simple_components
    download_btn, share_btn, go_advanced, numbering, qrcoding, go_download_share, simple_tab, enable_community_preset, community_preset, community_preset_input = others
    download_front, download_back, download_combine, share_front, share_back, share_combined = download_share_buttons
    front_raw, back_raw, combined_raw = raws

    render_inputs = [
        objekt,
        temp_id,
        cache_id,
        input_image,
        artist,
        season,
        classes,
        background_color,
        text_color,
        member,
        unit,
        numbering_state,
        number,
        alphabet,
        serial,
        qr_code,
    ]
    render_outputs = [
        objekt,
        temp_id,
        cache_id,
        input_image,
        download_front,
        download_back,
        download_combine,
        front_raw,
        back_raw,
        combined_raw,
    ]

    simple_plus_sync_outputs = []
    if simple_plus_components:
        (
            sp_artist,
            sp_season,
            sp_classes,
            sp_colors,
            sp_color_mode,
            sp_background_color,
            sp_image_options,
            sp_raw_sidebar,
            sp_raw_back,
            sp_ai_options,
            sp_ai_color,
            sp_ai_color_shape,
            sp_ai_color_seed,
            sp_ai_color_seed_type,
            sp_ai_generate,
            sp_ai_preview,
            sp_ai_sidebar,
            sp_ai_back,
            sp_text_color,
            sp_outline_color,
            sp_member,
            sp_logos,
            sp_top_logo,
            sp_side_logo,
            sp_sign,
            sp_sign_img,
            sp_sign_x,
            sp_sign_y,
            sp_sign_scale,
            sp_numbering,
            sp_number,
            sp_alphabet,
            sp_serial,
            sp_qrcoding,
            sp_qr_code,
            sp_qr_logo,
        ) = simple_plus_components
        simple_plus_sync_outputs = [
            sp_artist,
            sp_season,
            sp_classes,
            sp_color_mode,
            sp_background_color,
            sp_image_options,
            sp_raw_sidebar,
            sp_raw_back,
            sp_ai_options,
            sp_ai_preview,
            sp_ai_sidebar,
            sp_ai_back,
            sp_text_color,
            sp_outline_color,
            sp_member,
            sp_top_logo,
            sp_side_logo,
            sp_sign_img,
            sp_sign_x,
            sp_sign_y,
            sp_sign_scale,
            sp_numbering,
            sp_number,
            sp_alphabet,
            sp_serial,
            sp_qrcoding,
            sp_qr_code,
            sp_qr_logo,
        ]

    def sync_after(event):
        if not simple_plus_sync_outputs:
            return event
        return event.then(
            fn=sync_simple_to_simple_plus,
            inputs=objekt,
            outputs=simple_plus_sync_outputs,
        )

    go_advanced.click(fn=lambda: gr.Tabs(selected=1), inputs=None, outputs=tabs)
    go_download_share.click(fn=None, inputs=[], outputs=[], js=toggle_sidebar)

    sync_after(input_image.upload(
        fn=upload_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))

    sync_after(artist.input(
        fn=season_load,
        inputs=artist,
        outputs=[season, classes, member, unit, numbering, number, alphabet, serial, qrcoding, qr_code],
    ).then(
        fn=update_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))

    sync_after(community_preset_input.then(
        fn=season_load,
        inputs=artist,
        outputs=[season, classes, member, unit, numbering, number, alphabet, serial, qrcoding, qr_code],
    ).then(
        fn=update_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))


    sync_after(season.input(
        fn=class_load,
        inputs=[artist, season, classes],
        outputs=classes,
    ).then(
        fn=update_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))

    sync_after(classes.input(
        fn=member_load,
        inputs=[artist, season, classes],
        outputs=[member, unit, colors],
    ).then(
        fn=update_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))

    sync_after(member.input(
        fn=lambda: (gr.Group(visible=True), gr.Group(visible=True)),
        outputs=[numbering, qrcoding],
    ).then(
        fn=update_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))

    sync_after(unit.input(
        fn=lambda: (gr.Group(visible=True), gr.Group(visible=True)),
        outputs=[numbering, qrcoding],
    ).then(
        fn=update_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))

    for component in [number, alphabet, serial, qr_code]:
        sync_after(component.input(
            fn=update_simple_objekt,
            inputs=render_inputs,
            outputs=render_outputs,
        ))

    for component in [background_color, text_color]:
        sync_after(component.release(
            fn=update_simple_objekt,
            inputs=render_inputs,
            outputs=render_outputs,
        ))

    sync_after(numbering.expand(
        fn=lambda: gr.Checkbox(value=True),
        outputs=numbering_state,
    ).then(
        fn=update_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))
    sync_after(numbering.collapse(
        fn=lambda: gr.Checkbox(value=False),
        outputs=numbering_state,
    ).then(
        fn=update_simple_objekt,
        inputs=render_inputs,
        outputs=render_outputs,
    ))

    simple_tab.select(
        fn=lambda x, y, z: (
            gr.Row(visible=True),
            on_load(),
            gr.Radio(visible=False),
            gr.Dropdown(visible=False),
            gr.Radio(visible=False),
            gr.Dropdown(visible=False),
            gr.Checkbox(value=True),
            gr.Info('New features are here:\nSimple Plus (Full Edit) and Preset Maker are now available!', duration=5)
        )
        if not x
        else (
            gr.Row(visible=True),
            on_load(y, z),
            gr.Radio(),
            gr.Dropdown(),
            gr.Radio(),
            gr.Dropdown(),
            gr.Checkbox()
        ),
        inputs=[first_act, enable_community_preset, community_preset],
        outputs=[image_box, artist, classes, member, unit, community_preset, first_act],
    )
