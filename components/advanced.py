import gradio as gr




def build_ui(mode: str):
    """모드에 맞는 컴포넌트 리스트를 만들어 반환"""
    # 모드별 표시 설정만 딕셔너리로 관리
    CONFIG = {
        "Static": (True, False),
        "Colorful": (False, True),
        "None": (False, False)
    }


    cp1, cp2 = CONFIG.get(mode, CONFIG["Static"])
    return [
        gr.ColorPicker(visible=cp1),
        gr.Checkboxgroup(visible=cp2),
    ]


def advanced():
    with gr.Tab('Advanced', id=1) as advanced:
        with gr.Group('hidden', visible=False):
            pass

        gr.Markdown(value="Advanced is under development.")
        with gr.Column():
            with gr.Accordion(label='Colors', open=False):
                with gr.Row(equal_height=True):
                    with gr.Column():
                        color_type_choices = ['Static', 'Colorful', 'None']
                        color_type = gr.Radio(choices=color_type_choices, label='main', value=color_type_choices[0])

                        static_color = gr.ColorPicker(interactive=True, label='Main Color', value='#FFFFFF', visible=True)
                        colorful_color = gr.Checkboxgroup(interactive=True, label='Colorful Color', visible=False, choices=['Red', 'Yellow', 'Orange', 'Blue', 'Green', 'Purple'])

                        color_type.change(fn=build_ui, inputs=color_type, outputs=[static_color, colorful_color])

                    text_color = gr.ColorPicker(interactive=True, label='Text Color', value='#000000')



            with gr.Accordion(label='Texts', open=False):
                with gr.Row():
                    name = gr.Textbox(interactive=True, label='Name', value='', max_lines=1)
                    group_text = gr.Textbox(interactive=True, label='Group', value='', max_lines=1)

                with gr.Row():
                    class_ = gr.Textbox(interactive=True, label='Class', value='', max_lines=1)

                with gr.Row():
                    season = gr.Textbox(interactive=True, label='Season', value='', max_lines=1)
                    season_outline = gr.Textbox(interactive=True, label='Season outline', value='', max_lines=1)

            with gr.Accordion(label='Numbering', open=False):
                with gr.Row():
                    number = gr.Textbox(interactive=True, label='Number', value='', max_lines=1)
                    alphabet = gr.Textbox(interactive=True, label='Alphabet', value='', max_lines=1)
                    serial = gr.Textbox(interactive=True, label='Serial', value='', max_lines=1)

            with gr.Accordion(label='Sign', open=False):
                with gr.Row(equal_height=True):
                    sign = gr.Image(interactive=True, label='Sign', sources='upload')

                    with gr.Column():
                        sign_scale = gr.Slider(interactive=True, label='Scale', value=1, minimum=0.25, maximum=4, step=0.01)
                        sign_position_x = gr.Slider(interactive=True, label='X', value=0, minimum=0, maximum=1083, step=1)
                        sign_position_y = gr.Slider(interactive=True, label='Y', value=0, minimum=0, maximum=1673, step=1)




            with gr.Accordion(label='QR Code', open=False):
                qr_code = gr.Textbox(interactive=True, label='QR Code', max_lines=1)

                qr_logo = gr.Image(interactive=True, label='QR Logo', sources='upload')
                qr_caption = gr.Textbox(interactive=True, label='QR Caption', max_lines=1)

            with gr.Accordion(label='Group Logos', open=False):
                with gr.Row():
                    sidebar_logo = gr.Image(interactive=True, label='Sidebar logo', sources='upload')
                    top_logo = gr.Image(interactive=True, label='Top Logo', sources='upload')



            with gr.Accordion(label='Layouts', open=False, visible=False):
                with gr.Row():
                    front_layout = gr.Image(interactive=True, label='Front Layout', sources='upload')
                    back_layout = gr.Image(interactive=True, label='Back Layout', sources='upload')


    advanced_components = [color_type, static_color, colorful_color, text_color, name, group_text, class_, season, season_outline, number, alphabet, serial, sign, sign_scale, sign_position_x, sign_position_y, qr_code, qr_logo, qr_caption, sidebar_logo, top_logo, front_layout, back_layout]

    return advanced_components