import gradio as gr


def advanced():
    with gr.Tab('Advanced', id=1) as advanced:
        with gr.Group('hidden', visible=False):
            pass

        with gr.Column():
            with gr.Group():
                with gr.Row(equal_height=True):
                    main_color = gr.ColorPicker(label='Main Color', value='#FFFFFF', interactive=True)
                    text_color = gr.ColorPicker(label='Text Color', value='#000000', interactive=True)



            with gr.Group():
                with gr.Row(equal_height=True):
                    group_type = gr.Radio(choices=['Text', 'Image'], label='Group Type', value='Text')
                    group_text = gr.Text(label='Group')

                group_image = gr.Image(label='Group Image', visible=False, interactive=True)
                group_type.change(fn=lambda x: [gr.Text(visible=True), gr.Text(visible=False)] if x == 'Text' else [gr.Text(visible=False), gr.Text(visible=True)], inputs=group_type, outputs=[group_text, group_image])

            with gr.Group():
                with gr.Row():
                    number = gr.Textbox(label='Number', value='', interactive=True)
                    alphabet = gr.Textbox(label='Alphabet', value='', interactive=True)
                    serial = gr.Textbox(label='Serial', value='', interactive=True)


            with gr.Group():
                with gr.Row():
                    name = gr.Text(label='Name')

                with gr.Row():
                    class_ = gr.Text(label='Class')

                with gr.Row():
                    season = gr.Text(label='Season')
                    season_outline = gr.Text(label='Season outline')


            with gr.Group():
                with gr.Column():
                    sign_scale = gr.Slider(label='Sign Scale', value=50, minimum=0, maximum=100, step=1, interactive=True)
                    sign = gr.Image(label='Sign')




            with gr.Group():
                with gr.Column():
                    qr_code = gr.Text(label='QR Code')
                    qr_caption = gr.Text(label='QR Caption')

                with gr.Column():
                    qr_logo = gr.Image(label='Sign Logo')


            with gr.Accordion(label='Layouts', open=False):
                with gr.Row():
                    sidebar = gr.Image()
                    back_layout = gr.Image()

    return advanced