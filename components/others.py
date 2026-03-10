import gradio as gr
from html_elements import ads, preset_info
import config
from utils import check_blank
from .others_utils import color_components, add_class, class_tab_visible, class_tab_list, color_change, by_season_init, \
    class_name_change, season_select_change, class_select_select, json_update, all_seasons_have_class, sign_upload
from .steps import make_sign

def others(image_box):
    with gr.Tab('Preset Maker', id=2) as creator_tab:
        creator_tab.select(fn=lambda : gr.Row(visible=False), outputs=image_box)

        with gr.Row():
            with gr.Walkthrough() as walkthrough:
                with gr.Step("Start", id=0):
                    gr.Markdown(preset_info)

                    btn0 = gr.Button("Start!", interactive=True)
                    btn0.click(lambda: gr.Walkthrough(selected=4), outputs=walkthrough)

                with gr.Step("Artist", id=1):
                    group = gr.Textbox(label='Group Name', value='', interactive=True, min_width = 1)
                    members = gr.Dropdown(multiselect=True, allow_custom_value=True, label='Members', info='Write All members', value=['aaa', 'bb'])

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
                    btn3.click(lambda: gr.Walkthrough(selected=4), outputs=walkthrough)


                with gr.Step('Signs', id=4) as members_step:
                    make_sign(walkthrough, members, members_step, sign_upload)

                with gr.Step('Next', id=5):
                    pass

            color_json = gr.JSON(visible=False, value={}, open=True)
            color_json.change(fn=all_seasons_have_class, inputs=color_json, outputs=btn3)




            for colorpicker in [bc, tc]:
                colorpicker.input(fn=color_change, inputs=[seasons_select, class_select, bc, tc, color_json], outputs=color_json)




            class_name.change(fn=class_name_change, inputs=[seasons_select, class_name, color_json, bc, tc], outputs=[class_select, color_json])
            class_select.change(fn=class_select_select, inputs=[seasons_select, class_select, color_json], outputs=[bc, tc])
            by_season.select(fn=by_season_init, inputs=[add_seasons, color_json], outputs=[seasons_select, class_name, color_json])
            seasons_select.select(inputs=[seasons_select, color_json], outputs=class_name, fn=season_select_change)


            group.change(fn=json_update.group, inputs=[color_json, group], outputs=color_json)
            members.change(fn=json_update.members, inputs=[color_json, members], outputs=color_json)





    return

