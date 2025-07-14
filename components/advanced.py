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
                with gr.Row():
                    name = gr.Text(label='Name')
                    group_text = gr.Text(label='Group')

                with gr.Row():
                    class_ = gr.Text(label='Class')

                with gr.Row():
                    season = gr.Text(label='Season')
                    season_outline = gr.Text(label='Season outline')

            with gr.Group():
                with gr.Row():
                    number = gr.Textbox(label='Number', value='', interactive=True)
                    alphabet = gr.Textbox(label='Alphabet', value='', interactive=True)
                    serial = gr.Textbox(label='Serial', value='', interactive=True)

            with gr.Row():
                with gr.Group():
                    sign = gr.Image(label='Sign', sources='upload')
                    sign_scale = gr.Slider(label='Sign Scale', value=50, minimum=0, maximum=100, step=1, interactive=True)




                with gr.Group():
                    qr_code = gr.Text(label='QR Code')

                    qr_logo = gr.Image(label='QR Logo', sources='upload')
                    qr_caption = gr.Text(label='QR Caption')

            with gr.Accordion(label='Group Logos', open=False):
                with gr.Row():
                    sidebar_logo = gr.Image(label='Sidebar logo', sources='upload')
                    top_logo = gr.Image(label='Top Logo', sources='upload')



            with gr.Accordion(label='Layouts', open=False):
                with gr.Row():
                    sidebar = gr.Image(label='Sidebar', sources='upload')
                    back_layout = gr.Image(label='Back Layout', sources='upload')

    return advanced