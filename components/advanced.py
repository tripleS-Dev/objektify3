import gradio as gr


def advanced():
    with gr.Tab('Advanced', id=1) as advanced:
        with gr.Group('hidden', visible=False):
            pass

        with gr.Column():
            with gr.Accordion(label='Colors', open=False):
                with gr.Row(equal_height=True):
                    main_color = gr.ColorPicker(interactive=True, label='Main Color', value='#FFFFFF')
                    text_color = gr.ColorPicker(interactive=True, label='Text Color', value='#000000')



            with gr.Accordion(label='Texts', open=False):
                with gr.Row():
                    name = gr.Text(interactive=True, label='Name')
                    group_text = gr.Text(interactive=True, label='Group')

                with gr.Row():
                    class_ = gr.Text(interactive=True, label='Class')

                with gr.Row():
                    season = gr.Text(interactive=True, label='Season')
                    season_outline = gr.Text(interactive=True, label='Season outline')

            with gr.Accordion(label='Numbering', open=False):
                with gr.Row():
                    number = gr.Textbox(interactive=True, label='Number', value='')
                    alphabet = gr.Textbox(interactive=True, label='Alphabet', value='')
                    serial = gr.Textbox(interactive=True, label='Serial', value='')

            with gr.Accordion(label='Sign', open=False):
                with gr.Row(equal_height=True):
                    sign = gr.Image(interactive=True, label='Sign', sources='upload')

                    with gr.Column():
                        sign_scale = gr.Slider(interactive=True, label='Scale', value=1, minimum=0.25, maximum=4, step=0.01)
                        sign_position_x = gr.Slider(interactive=True, label='X', value=0, minimum=0, maximum=1083, step=1)
                        sign_position_y = gr.Slider(interactive=True, label='Y', value=0, minimum=0, maximum=1673, step=1)




            with gr.Accordion(label='QR Code', open=False):
                qr_code = gr.Text(interactive=True, label='QR Code')

                qr_logo = gr.Image(interactive=True, label='QR Logo', sources='upload')
                qr_caption = gr.Text(interactive=True, label='QR Caption')

            with gr.Accordion(label='Group Logos', open=False):
                with gr.Row():
                    sidebar_logo = gr.Image(interactive=True, label='Sidebar logo', sources='upload')
                    top_logo = gr.Image(interactive=True, label='Top Logo', sources='upload')



            with gr.Accordion(label='Layouts', open=False):
                with gr.Row():
                    sidebar = gr.Image(interactive=True, label='Sidebar', sources='upload')
                    back_layout = gr.Image(interactive=True, label='Back Layout', sources='upload')


    advanced_components = [main_color, text_color, name, group_text, class_, season, season_outline, number, alphabet, serial, sign, sign_scale, sign_position_x, sign_position_y, qr_code, qr_logo, qr_caption, sidebar_logo, top_logo, sidebar, back_layout]

    return advanced_components