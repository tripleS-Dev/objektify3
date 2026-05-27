from generate.modhaus.simple_callbacks import (
    simple_plus_color_mode_input,
    update_simple_plus_objekt,
)
from generate.simple_plus import make_ai_gradient


def simple_plus(
    objekt,
    temp_id,
    cache_id,
    input_image,
    simple_plus_components,
    download_share_buttons,
    raws,
):
    (
        artist,
        season,
        classes,
        colors,
        color_mode,
        background_color,
        image_options,
        raw_sidebar,
        raw_back,
        ai_options,
        ai_color,
        ai_color_shape,
        ai_color_seed,
        ai_color_seed_type,
        ai_generate,
        ai_preview,
        ai_sidebar,
        ai_back,
        text_color,
        outline_color,
        member,
        logos,
        top_logo,
        side_logo,
        sign,
        sign_img,
        sign_x,
        sign_y,
        sign_scale,
        numbering,
        number,
        alphabet,
        serial,
        qrcoding,
        qr_code,
        qr_logo,
    ) = simple_plus_components
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
        color_mode,
        background_color,
        text_color,
        outline_color,
        member,
        number,
        alphabet,
        serial,
        qr_code,
        top_logo,
        side_logo,
        sign_img,
        sign_x,
        sign_y,
        sign_scale,
        qr_logo,
        raw_sidebar,
        raw_back,
        ai_sidebar,
        ai_back,
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

    def render_after(event):
        return event.then(
            fn=update_simple_plus_objekt,
            inputs=render_inputs,
            outputs=render_outputs,
        )

    render_after(color_mode.input(
        fn=simple_plus_color_mode_input,
        inputs=color_mode,
        outputs=[image_options, ai_options, background_color],
    ))

    render_after(ai_generate.click(
        fn=make_ai_gradient,
        inputs=[ai_color, ai_color_shape, ai_color_seed],
        outputs=[ai_preview, ai_sidebar, ai_back],
    ))

    for component in [artist, season, classes, member, number, alphabet, serial, qr_code]:
        component.blur(
            fn=update_simple_plus_objekt,
            inputs=render_inputs,
            outputs=render_outputs,
        )


    for component in [sign_x, sign_y]:
        component.input(
            fn=update_simple_plus_objekt,
            inputs=render_inputs,
            outputs=render_outputs,
        )

    for component in [background_color, text_color, outline_color, sign_scale]:
        component.release(
            fn=update_simple_plus_objekt,
            inputs=render_inputs,
            outputs=render_outputs,
        )

    for component in [raw_sidebar, raw_back, top_logo, side_logo, sign_img, qr_logo]:
        component.input(
            fn=update_simple_plus_objekt,
            inputs=render_inputs,
            outputs=render_outputs,
        )
