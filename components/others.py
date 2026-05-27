from pathlib import Path

import gradio as gr

from generate.modhaus.preset import Preset
from html_elements import preset_info
from utils import list_artist_folders

from .others_utils import preset_callbacks as pc


def others(image_box):
    with gr.Tab("Preset Maker", id=2) as creator_tab:
        creator_tab.select(fn=lambda: gr.Row(visible=False), outputs=image_box)

        preset_state = gr.State(Preset.new())

        with gr.Row(equal_height=False):
            with gr.Column(scale=3):
                with gr.Walkthrough() as walkthrough:
                    with gr.Step("Start", id=0):
                        gr.Markdown(preset_info)

                        mode = gr.Radio(
                            choices=["Create New", "Edit Existing"],
                            value="Create New",
                            label="Mode",
                            interactive=True,
                        )

                        create_btn = gr.Button("Create New Preset", variant="primary")

                        with gr.Group(visible=False) as edit_group:
                            edit_preset = gr.Dropdown(
                                label="Community Preset",
                                choices=list_artist_folders(False),
                                interactive=True,
                            )
                            edit_password = gr.Textbox(
                                label="Password",
                                type="password",
                                interactive=True,
                            )
                            load_btn = gr.Button("Load for Editing", variant="primary", visible=False)

                    with gr.Step("Artist", id=1):
                        group = gr.Textbox(label="Group Name", value="", interactive=True, min_width=1)
                        members = gr.Dropdown(
                            multiselect=True,
                            allow_custom_value=True,
                            label="Members",
                            info="Write all members",
                        )

                        btn1 = gr.Button("Next", interactive=False, variant="secondary")
                        btn1.click(lambda: gr.Walkthrough(selected=2), outputs=walkthrough)

                    with gr.Step("Season", id=2):
                        add_seasons = gr.Dropdown(
                            multiselect=True,
                            allow_custom_value=True,
                            label="Seasons",
                            info="Write all seasons. If you use /, the characters following it will use an outlined font.",
                        )

                        btn2 = gr.Button("Next", interactive=False, variant="secondary")
                        btn2.click(lambda: gr.Walkthrough(selected=3), outputs=walkthrough)

                    with gr.Step("Class", id=3) as by_season:
                        seasons_select = gr.Radio(
                            choices=[],
                            interactive=True,
                            label="Season",
                            info="Select season to edit",
                        )

                        with gr.Group():
                            class_name = gr.Dropdown(
                                label="Class Name",
                                interactive=True,
                                allow_custom_value=True,
                                multiselect=True,
                                max_choices=10,
                            )
                            class_select = gr.Radio(
                                label="Class",
                                info="Select class to edit",
                                interactive=True,
                            )

                        with gr.Row(equal_height=True):
                            bc = gr.ColorPicker(
                                label="Background Color",
                                interactive=True,
                                visible=True,
                                value="#FFFFFF",
                                min_width=260,
                            )
                            tc = gr.ColorPicker(
                                label="Text Color",
                                interactive=True,
                                visible=True,
                                value="#000000",
                                min_width=260,
                            )

                        btn3 = gr.Button("Next", interactive=False, variant="secondary")
                        btn3.click(lambda: gr.Walkthrough(selected=4), outputs=walkthrough)

                    with gr.Step("Signs", id=4):
                        with gr.Row(equal_height=True):
                            with gr.Column():
                                members_radio = gr.Radio(
                                    choices=[],
                                    label="Member",
                                    interactive=True,
                                )
                                sign_file = gr.File(
                                    file_count="single",
                                    file_types=[".png", ".webp", ".svg", ".jpeg", ".jpg"],
                                    interactive=True,
                                    height=120,
                                    label="Upload Sign",
                                )
                                with gr.Row(equal_height=True):
                                    sing_x = gr.Slider(label="X", minimum=-100, maximum=100, step=1, value=0)
                                    sing_y = gr.Slider(label="Y", minimum=-100, maximum=100, step=1, value=0)
                                    sing_size = gr.Slider(label="Size", minimum=10, maximum=200, step=1, value=100)
                                remove_bg = gr.Checkbox(
                                    label="Remove Background",
                                    info="Use this if the sign image has a background.",
                                )
                                apply_sign_btn = gr.Button("Apply Sign", variant="primary")

                            sign_preview = gr.Image(
                                visible=True,
                                image_mode="RGBA",
                                sources=["upload", "clipboard"],
                                type="pil",
                                buttons=None,
                                format="png",
                                interactive=False,
                                label="Preview",
                                height="100%",
                                elem_classes="sticky-image-small",
                            )

                        btn4 = gr.Button("Next", interactive=True, variant="primary")
                        btn4.click(lambda: gr.Walkthrough(selected=5), outputs=walkthrough)

                    with gr.Step("Logos", id=5):
                        with gr.Column():
                            with gr.Accordion("Adding a Top Logo is recommended.", open=True) as top_accordion:
                                with gr.Row(equal_height=True):
                                    with gr.Column():
                                        top_logo = gr.Image(
                                            label="Top Logo (Optional)",
                                            height=200,
                                            type="filepath",
                                            buttons=None,
                                            sources="upload",
                                        )
                                        with gr.Row(equal_height=True):
                                            top_logo_scale = gr.Slider(label="Scale", step=1, minimum=1, maximum=400, value=100)
                                            top_logo_removebg = gr.Checkbox(label="Remove Background")
                                    top_logo_preview = gr.Image(
                                        buttons=None,
                                        interactive=False,
                                        height=200,
                                        label="Preview",
                                        value=f"{Path(__file__).resolve().parent.parent}/utils/resources/top_logo_preview.png",
                                    )

                            with gr.Accordion("Adding a QR Logo", open=False) as qr_accordion:
                                with gr.Row(equal_height=True):
                                    qr_logo = gr.Image(
                                        label="QR Logo (Optional)",
                                        height=200,
                                        type="filepath",
                                        buttons=None,
                                        sources="upload",
                                    )
                                    qr_logo_preview = gr.Image(
                                        buttons=None,
                                        interactive=False,
                                        height=200,
                                        label="Preview",
                                        value=f"{Path(__file__).resolve().parent.parent}/utils/resources/qr_logo_preview.png",
                                    )

                            with gr.Accordion("Side Logo (Leaving it blank is recommended.)", open=False) as side_accordion:
                                with gr.Row(equal_height=True):
                                    with gr.Column():
                                        side_logo = gr.Image(
                                            label="Side Logo (Optional)",
                                            height=200,
                                            type="filepath",
                                            buttons=None,
                                            sources="upload",
                                        )
                                        with gr.Row(equal_height=True):
                                            side_logo_scale = gr.Slider(label="Scale", step=1, minimum=-10, maximum=10, value=0)
                                            side_logo_removebg = gr.Checkbox(label="Remove Background")

                                    side_logo_preview = gr.Image(buttons=None, interactive=False, height=200, label="Preview")

                            accordions = [top_accordion, qr_accordion, side_accordion]
                            for i, accordion in enumerate(accordions):
                                accordion.expand(
                                    fn=lambda i=i: (
                                        gr.Accordion(open=(i == 0)),
                                        gr.Accordion(open=(i == 1)),
                                        gr.Accordion(open=(i == 2)),
                                    ),
                                    inputs=[],
                                    outputs=accordions,
                                    queue=False,
                                )

                        btn5 = gr.Button("Next", interactive=True, variant="primary")
                        btn5.click(lambda: gr.Walkthrough(selected=6), outputs=walkthrough)

                    with gr.Step("Defaults", id=6):
                        gr.HTML("It will be displayed when users don't select any options. If it is blank, it will be displayed in white.")
                        with gr.Row():
                            with gr.Column():
                                with gr.Row(equal_height=True):
                                    default_color_side = gr.ColorPicker(
                                        label="Default Side Color",
                                        value="#FFFFFF",
                                        min_width=260,
                                        interactive=True,
                                    )
                                    default_color_text = gr.ColorPicker(
                                        label="Default Text Color",
                                        value="#000000",
                                        min_width=260,
                                        interactive=True,
                                    )

                                default_img = gr.Image(label="Default Objekt Image", type="pil", interactive=True, height="30dvh")
                                batch_type = gr.Radio(
                                    choices=["Center of container", "Center of viewport"],
                                    value="Center of container",
                                )

                            default_img_preview = gr.Image(
                                buttons=None,
                                interactive=False,
                                label="Preview",
                                value=f"{Path(__file__).resolve().parent.parent}/utils/resources/front_preview.png",
                                height="50dvh",
                            )

                        btn6 = gr.Button("Next", interactive=True, variant="primary")
                        btn6.click(lambda: gr.Walkthrough(selected=7), outputs=walkthrough)

                    with gr.Step("Submit", id=7):
                        with gr.Row():
                            with gr.Column():
                                creator_name = gr.Textbox(label="Creator Name", info="This name will be displayed to users.")
                                password = gr.Textbox(
                                    interactive=True,
                                    label="Password",
                                    info="Required for new presets. Leave blank while editing to keep the existing password.",
                                    type="password",
                                )
                                password_confirm = gr.Textbox(interactive=True, label="Password Confirm", type="password")
                                password_show = gr.Checkbox(label="Show Password")

                                password_show.change(
                                    lambda x: (gr.Textbox(type="text"), gr.Textbox(type="text"))
                                    if x
                                    else (gr.Textbox(type="password"), gr.Textbox(type="password")),
                                    inputs=password_show,
                                    outputs=[password, password_confirm],
                                )

                            with gr.Accordion("Contact Information (Recommended)", open=True):
                                gr.Markdown(
                                    "This field allows administrators to contact you if there are any issues, "
                                    "such as modifications to presets or promotion to official status."
                                )
                                discord_id = gr.Textbox(label="Discord ID (Optional)")
                                email_id = gr.Textbox(label="Email (Optional)", type="email")

                        submit_btn = gr.Button("Submit", variant="primary", interactive=True)
                        submit_result = gr.Markdown()

            with gr.Column(scale=1):
                status_panel = gr.Markdown(value=pc.status_markdown(Preset.new()))
                sign_status = gr.Dataframe(
                    headers=pc.SIGN_STATUS_HEADERS,
                    value=[],
                    interactive=False,
                    label="Sign Status",
                    wrap=True,
                )
                debug_config = gr.JSON(
                    label="Config Preview",
                    value=Preset.new().to_config(),
                    open=False,
                )

        mode.change(fn=pc.toggle_start_mode, inputs=mode, outputs=[edit_group, create_btn, load_btn, edit_preset])

        create_btn.click(
            fn=pc.create_new_preset,
            outputs=[
                preset_state,
                group,
                members,
                add_seasons,
                seasons_select,
                class_name,
                class_select,
                members_radio,
                creator_name,
                discord_id,
                email_id,
                default_color_side,
                default_color_text,
                top_logo_preview,
                qr_logo_preview,
                side_logo_preview,
                default_img_preview,
                btn1,
                status_panel,
                sign_status,
                debug_config,
                walkthrough,
            ],
        )

        load_btn.click(
            fn=pc.load_existing_preset,
            inputs=[preset_state, edit_preset, edit_password],
            outputs=[
                preset_state,
                group,
                members,
                add_seasons,
                seasons_select,
                class_name,
                class_select,
                members_radio,
                creator_name,
                discord_id,
                email_id,
                default_color_side,
                default_color_text,
                top_logo_preview,
                qr_logo_preview,
                side_logo_preview,
                default_img_preview,
                btn1,
                status_panel,
                sign_status,
                debug_config,
                walkthrough,
            ],
        )

        group.input(
            fn=pc.set_identity,
            inputs=[preset_state, group, members],
            outputs=[preset_state, btn1, members_radio, status_panel, sign_status, debug_config],
        )
        members.change(
            fn=pc.set_identity,
            inputs=[preset_state, group, members],
            outputs=[preset_state, btn1, members_radio, status_panel, sign_status, debug_config],
        )

        add_seasons.change(
            fn=pc.set_seasons,
            inputs=[preset_state, add_seasons],
            outputs=[preset_state, btn2, seasons_select, class_name, class_select, status_panel, sign_status, debug_config],
        )

        seasons_select.select(
            fn=pc.select_season,
            inputs=[preset_state, seasons_select],
            outputs=[class_name, class_select, bc, tc],
        )
        class_name.change(
            fn=pc.set_classes,
            inputs=[preset_state, seasons_select, class_name, bc, tc],
            outputs=[preset_state, class_select, btn3, status_panel, sign_status, debug_config],
        )
        class_select.input(
            fn=pc.select_class,
            inputs=[preset_state, seasons_select, class_select],
            outputs=[bc, tc],
        )
        for colorpicker in [bc, tc]:
            colorpicker.release(
                fn=pc.set_class_color,
                inputs=[preset_state, seasons_select, class_select, bc, tc],
                outputs=[preset_state, status_panel, sign_status, debug_config],
            )

        members_radio.select(
            fn=pc.select_sign_member,
            inputs=[preset_state, members_radio],
            outputs=[sign_preview, sing_x, sing_y, sing_size],
        )
        apply_sign_btn.click(
            fn=pc.apply_sign,
            inputs=[preset_state, members_radio, sign_file, sing_x, sing_y, sing_size, remove_bg],
            outputs=[preset_state, sign_preview, status_panel, sign_status, debug_config],
        )

        top_logo.change(
            fn=pc.set_top_logo,
            inputs=[preset_state, top_logo, top_logo_scale, top_logo_removebg],
            outputs=[preset_state, top_logo_preview, status_panel, sign_status, debug_config],
        )
        top_logo_scale.release(
            fn=pc.set_top_logo,
            inputs=[preset_state, top_logo, top_logo_scale, top_logo_removebg],
            outputs=[preset_state, top_logo_preview, status_panel, sign_status, debug_config],
        )
        top_logo_removebg.change(
            fn=pc.set_top_logo,
            inputs=[preset_state, top_logo, top_logo_scale, top_logo_removebg],
            outputs=[preset_state, top_logo_preview, status_panel, sign_status, debug_config],
        )
        qr_logo.change(
            fn=pc.set_qr_logo,
            inputs=[preset_state, qr_logo],
            outputs=[preset_state, qr_logo_preview, status_panel, sign_status, debug_config],
        )
        side_logo.change(
            fn=pc.set_side_logo,
            inputs=[preset_state, side_logo, side_logo_scale, side_logo_removebg],
            outputs=[preset_state, side_logo_preview, status_panel, sign_status, debug_config],
        )
        side_logo_scale.release(
            fn=pc.set_side_logo,
            inputs=[preset_state, side_logo, side_logo_scale, side_logo_removebg],
            outputs=[preset_state, side_logo_preview, status_panel, sign_status, debug_config],
        )
        side_logo_removebg.change(
            fn=pc.set_side_logo,
            inputs=[preset_state, side_logo, side_logo_scale, side_logo_removebg],
            outputs=[preset_state, side_logo_preview, status_panel, sign_status, debug_config],
        )

        for default_component in [default_color_side, default_color_text]:
            default_component.release(
                fn=pc.set_default,
                inputs=[preset_state, default_color_side, default_color_text, default_img, batch_type],
                outputs=[preset_state, default_img_preview, status_panel, sign_status, debug_config],
            )
        for default_component in [default_img, batch_type]:
            default_component.change(
                fn=pc.set_default,
                inputs=[preset_state, default_color_side, default_color_text, default_img, batch_type],
                outputs=[preset_state, default_img_preview, status_panel, sign_status, debug_config],
            )

        submit_btn.click(
            fn=pc.submit_preset,
            inputs=[
                preset_state,
                creator_name,
                password,
                password_confirm,
                discord_id,
                email_id,
                default_color_side,
                default_color_text,
            ],
            outputs=[preset_state, submit_result, edit_preset, status_panel, sign_status, debug_config],
        )

    return
