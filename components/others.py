import gradio as gr
from html_elements import ads
import config
from utils import check_blank
from .others_utils import color_components, add_class, class_tab_visible, class_tab_list, color_change, by_season_init


def others(image_box):
    with gr.Tab('Preset Maker', id=2) as creator_tab:
        creator_tab.select(fn=lambda : gr.Row(visible=False), outputs=image_box)


        with gr.Walkthrough() as walkthrough:
            with gr.Step("Artist", id=0):
                group = gr.Textbox(label='Group Name', value='', interactive=True, min_width = 1)
                memebrs = gr.Dropdown(multiselect=True, allow_custom_value=True, label='Members', info='Write All members')

                btn0 = gr.Button("Next", interactive=False)
                btn0.click(lambda: gr.Walkthrough(selected=1), outputs=walkthrough)


                group.change(fn=check_blank, inputs=[group, memebrs], outputs=btn0)
                memebrs.change(fn=check_blank, inputs=[group, memebrs], outputs=btn0)


            with gr.Step("Season", id=1):
                add_seasons = gr.Dropdown(multiselect=True, allow_custom_value=True, label='Seasons', info='Write All seasons\nFor example: Spring26, Summer26, 1st Album, 2nd Mini')

                btn1 = gr.Button("Next", interactive=False)
                btn1.click(lambda: gr.Walkthrough(selected=2), outputs=walkthrough)

                add_seasons.change(fn=check_blank, inputs=add_seasons, outputs=btn1)

            with gr.Step('By season', id=2) as by_season:
                seasons_select = gr.Radio(choices=None, interactive=True, label='Season', info='Select season to edit')



                with gr.Group():
                    class_name = gr.Dropdown(label='Class Name', interactive=True, allow_custom_value=True, multiselect=True, max_choices=10)
                    class_select = gr.Radio(label='Class', info='Select class to edit', interactive=True)

                    class_name.change(fn=lambda x: gr.Radio(choices=x, value=x[0] if len(x) >= 1 else None), inputs=class_name, outputs=class_select)


                with gr.Group():
                    bc = gr.ColorPicker(label='Background Color', interactive=True, visible=True, value='#FFFFFF', min_width=260)  # width 너무 작으면 모바일에서 깨짐
                    tc = gr.ColorPicker(label='Text Color', interactive=True, visible=True, value='#000000', min_width=260)

                color_json = gr.JSON(visible=True, value={})

                for colorpicker in [bc, tc]:
                    colorpicker.change(fn=color_change, inputs=[seasons_select, class_select, bc, tc, color_json], outputs=color_json)
                #class_select.select(fn=lambda x,y: x, inputs=[class_name, class_select], outputs=colors)

                by_season.select(fn=by_season_init, inputs=add_seasons, outputs=[seasons_select, class_name, color_json])


    return

