

def advanced(input_image_raw, input_image, advanced_components, true=None, false=None, demo=None, difficult=None):
    main_color, text_color, name, group_text, class_, season, season_outline, number, alphabet, serial, sign, sign_scale, sign_position_x, sign_position_y, qr_code, qr_logo, qr_caption, sidebar_logo, top_logo, sidebar, back_layout = advanced_components

    if not any(advanced_components):
        for component in advanced_components:
            component.input(fn=make_json, inputs=all_components, outputs=[input_image, download_btn] + advanced_components)




    pass