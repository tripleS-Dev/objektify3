import gradio as gr
from html_elements import ads, preset_info
import config
from utils import check_blank, logo_upload, sort_seasons
from utils.logo_upload import side
from .others_utils import color_components, add_class, class_tab_visible, class_tab_list, color_change, by_season_init, \
    class_name_change, season_select_change, class_select_select, json_update, all_seasons_have_class, sign_upload, \
    make_default_preview, submit
from .steps import make_sign
from pathlib import Path

json_init = {
  "official": False,
  "side_logo": False,
  "top_logo": False,
  "qr_logo": False,
  "default": False,
}

def others(image_box):
    with gr.Tab('Preset Maker', id=2) as creator_tab:
        creator_tab.select(fn=lambda : gr.Row(visible=False), outputs=image_box)

        with gr.Row():
            with gr.Walkthrough() as walkthrough:
                with gr.Step("Start", id=0):
                    gr.Markdown(preset_info)

                    btn0 = gr.Button("Start!", interactive=True)
                    color_json = gr.JSON(visible=True, value=json_init, open=True)
                    btn0.click(lambda: gr.Walkthrough(selected=7), outputs=walkthrough)

                with gr.Step("Artist", id=1):
                    group = gr.Textbox(label='Group Name', value='', interactive=True, min_width = 1)
                    members = gr.Dropdown(multiselect=True, allow_custom_value=True, label='Members', info='Write All members')

                    btn1 = gr.Button("Next", interactive=False)
                    btn1.click(lambda: gr.Walkthrough(selected=2), outputs=walkthrough)


                    group.change(fn=check_blank, inputs=[group, members], outputs=btn1)
                    members.change(fn=check_blank, inputs=[group, members], outputs=btn1)


                with gr.Step("Season", id=2):
                    add_seasons = gr.Dropdown(multiselect=True, allow_custom_value=True, label='Seasons', info='Write All seasons\nIf you use /, the characters following it will use an outlined font.\n\nFor example: Spring/26, Summer/26, 1st Album, 2nd Mini\n')

                    btn2 = gr.Button("Next", interactive=False)
                    btn2.click(lambda: gr.Walkthrough(selected=3), outputs=walkthrough)

                    add_seasons.change(fn=check_blank, inputs=add_seasons, outputs=btn2)

                with gr.Step('Class', id=3) as by_season:
                    seasons_select = gr.Radio(choices=None, interactive=True, label='Season', info='Select season to edit')



                    with gr.Group():
                        class_name = gr.Dropdown(label='Class Name', interactive=True, allow_custom_value=True, multiselect=True, max_choices=10)
                        class_select = gr.Radio(label='Class', info='Select class to edit', interactive=True)

                    with gr.Group():
                        with gr.Row(equal_height=True):
                            bc = gr.ColorPicker(label='Background Color', interactive=True, visible=True, value='#FFFFFF', min_width=260)  # width 너무 작으면 모바일에서 깨짐
                            tc = gr.ColorPicker(label='Text Color', interactive=True, visible=True, value='#000000', min_width=260)

                    btn3 = gr.Button("Next", interactive=False)
                    btn3.click(lambda: gr.Walkthrough(selected=4), outputs=walkthrough).then(fn=sort_seasons, inputs=[color_json, add_seasons], outputs=color_json)


                with gr.Step('Signs', id=4) as members_step:
                    sign_save = make_sign(walkthrough, color_json, members, members_step, sign_upload)

                with gr.Step('Logos', id=5):
                    with gr.Column():
                        with gr.Accordion("Adding a Top Logo is recommended.", open=True) as top_accordion:
                            with gr.Row(equal_height=True):
                                #gr.HTML("Adding a Top Logo is recommended.")
                                with gr.Column():
                                    top_logo = gr.Image(label='Top Logo (Optional)', height=200, type='filepath', buttons=None, sources='upload')
                                    top_logo_save = gr.Image(type='pil',interactive=False, visible=True, image_mode='RGBA')
                                    with gr.Row(equal_height=True):
                                        top_logo_scale = gr.Slider(label='Scale', step=1, minimum=1, maximum=400, value=100)
                                        top_logo_removebg = gr.Checkbox(label='Remove Background', info='If image has background, you can use this.\nIt can Fix white image')
                                top_logo_preview = gr.Image(buttons=None, interactive=False, height=200, label='Preview', value=f'{Path(__file__).resolve().parent.parent}/utils/resources/top_logo_preview.png')


                                top_logo.change(fn=logo_upload.top, inputs=[color_json, top_logo, top_logo_scale, top_logo_removebg], outputs=[top_logo_preview, top_logo_save, color_json])
                                top_logo_removebg.change(fn=logo_upload.top, inputs=[color_json, top_logo, top_logo_scale, top_logo_removebg], outputs=[top_logo_preview, top_logo_save, color_json])
                                top_logo_scale.release(fn=logo_upload.top, inputs=[color_json, top_logo, top_logo_scale, top_logo_removebg], outputs=[top_logo_preview, top_logo_save, color_json])

                        with gr.Accordion("Adding a QR Logo", open=False) as qr_accordion:
                            with gr.Row(equal_height=True):
                                #gr.HTML("<br>The QR code can still be recognized even with a logo here.")
                                qr_logo = gr.Image(label='QR Logo (Optional)', height=200, type='filepath', buttons=None, sources='upload') #, info='(Optional)The QR code can still be recognized even with a logo here.'
                                qr_logo_save = gr.Image(type='pil',interactive=False, visible=False, image_mode='RGBA')

                                qr_logo_preview = gr.Image(buttons=None, interactive=False, height=200, label='Preview', value=f'{Path(__file__).resolve().parent.parent}/utils/resources/qr_logo_preview.png')

                                qr_logo.change(fn=logo_upload.qr, inputs=[color_json    , qr_logo], outputs=[qr_logo_preview, qr_logo_save, color_json])

                        with gr.Accordion("Side Logo (Leaving it blank is recommended.)", open=False) as side_accordion:
                            with gr.Row(equal_height=True):
                                #gr.HTML("<br>Leaving it blank is recommended.<br>This logo appears on the right instead of the group name text.")
                                with gr.Column():
                                    side_logo = gr.Image(label='Side Logo (Optional)', height=200, type='filepath', buttons=None, sources='upload') #, info='(Optional)\nThis logo appears on the right instead of the group name text. Leaving it blank is recommended.'
                                    side_logo_save = gr.Image(type='pil',interactive=False, visible=False, image_mode='RGBA')
                                    with gr.Row(equal_height=True):
                                        side_logo_scale = gr.Slider(label='Scale', step=1, minimum=-10, maximum=10, value=0)
                                        side_logo_removebg = gr.Checkbox(label='Remove Background', info='If image has background, you can use this.\nIt can Fix white image')

                                side_logo_preview = gr.Image(buttons=None, interactive=False, height=200, label='Preview')

                                side_logo_inputs = [color_json, side_logo, side_logo_scale, side_logo_removebg]
                                side_logo_outputs = [side_logo_preview, side_logo_save, color_json]

                                side_logo.change(fn=logo_upload.side, inputs=side_logo_inputs, outputs=side_logo_outputs)
                                side_logo_scale.release(fn=logo_upload.side, inputs=side_logo_inputs, outputs=side_logo_outputs)
                                side_logo_removebg.change(fn=logo_upload.side, inputs=side_logo_inputs, outputs=side_logo_outputs)

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

                    btn5 = gr.Button("Next", interactive=True, variant='primary')
                    btn5.click(lambda: gr.Walkthrough(selected=6), outputs=walkthrough)

                with gr.Step('Defaults', id=6):
                    gr.HTML("""It will be displayed when users dont select any options.\nIf it is blank, it will be displayed in white.""")
                    with gr.Row():
                        with gr.Column():
                            with gr.Group():
                                with gr.Row(equal_height=True):
                                    default_color_side = gr.ColorPicker(label="Default Side Color", value='#C1D1F2', min_width = 260, interactive=True)
                                    default_color_text = gr.ColorPicker(label="Default Text Color", value='#000000', min_width = 260, interactive=True)

                            with gr.Group():
                                default_img = gr.Image(label='Default Objekt Image', type='pil', interactive=True, height='30dvh')
                                batch_type = gr.Radio(choices=['Center of container', 'Center of viewport'], value='Center of container')

                        default_img_preview = gr.Image(buttons=None, interactive=False, label='Preview', value=f'{Path(__file__).resolve().parent.parent}/utils/resources/front_preview.png', height='50dvh')
                        default_img_save = gr.Image(type='pil',interactive=False, visible=False, image_mode='RGBA')

                    for default_component in [default_color_side, default_color_text]:
                        default_component.release(fn=make_default_preview, inputs=[default_color_side, default_color_text, default_img, batch_type], outputs=[default_img_preview, default_img_save])

                    for default_component2 in [default_img, batch_type]:
                        default_component2.change(fn=make_default_preview, inputs=[default_color_side, default_color_text, default_img, batch_type], outputs=[default_img_preview, default_img_save])

                    btn6 = gr.Button("Next", interactive=True, variant='primary')
                    btn6.click(lambda: gr.Walkthrough(selected=7), outputs=walkthrough)

                with gr.Step('Submit', id=7):
                    with gr.Row():
                        with gr.Column():
                            creator_name = gr.Textbox(label='Creator Name', info='This name will be displayed to users.')
                            password = gr.Textbox(interactive=True, label='Password', info='This password is required to edit or delete presets.', type="password")
                            password_confirm = gr.Textbox(interactive=True, label='Password Confirm', info='password confirm', type="password")
                            password_show = gr.Checkbox(label="Show Password")

                            password_show.change(lambda x: (gr.Textbox(type='text'), gr.Textbox(type='text'))if x else (gr.Textbox(type='password'), gr.Textbox(type='password')), inputs=password_show, outputs=[password, password_confirm])

                        with gr.Accordion('Contact Information (Recommended)', open=True):
                            gr.Markdown('This field allows administrators to contact you if there are any issues, such as modifications to presets or promotion to official status.\n\nProviding this information is optional. If left blank, administrators may modify or remove your content without prior notice.\n\nThis information will only be visible to administrators.')

                            with gr.Column():
                                discord_id = gr.Textbox(label='Discord ID (Optional)', info='Not a nickname, but a username that can be added as a friend.')
                                email_id = gr.Textbox(label='Email (Optional)', type='email')

                        with gr.Group():
                            submit_btn = gr.Button('Submit', variant='secondary', interactive=True)


            submit_btn.click(fn=submit, inputs=[creator_name, password, discord_id, email_id, color_json, default_color_side, default_color_text, default_img_save, top_logo_save, qr_logo_save, side_logo_save, sign_save])

            color_json.change(fn=all_seasons_have_class, inputs=color_json, outputs=btn3)




            for colorpicker in [bc, tc]:
                colorpicker.release(fn=color_change, inputs=[seasons_select, class_select, bc, tc, color_json], outputs=color_json)




            class_name.change(fn=class_name_change, inputs=[seasons_select, class_name, color_json, bc, tc], outputs=[class_select, color_json])
            class_select.change(fn=class_select_select, inputs=[seasons_select, class_select, color_json], outputs=[bc, tc])
            by_season.select(fn=by_season_init, inputs=[add_seasons, color_json], outputs=[seasons_select, class_name, color_json])
            seasons_select.select(inputs=[seasons_select, color_json], outputs=class_name, fn=season_select_change)


            group.change(fn=json_update.group, inputs=[color_json, group], outputs=color_json)
            members.change(fn=json_update.members, inputs=[color_json, members], outputs=color_json)





    return

