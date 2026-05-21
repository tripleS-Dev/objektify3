import gradio as gr

def make_sign(walkthrough, color_json, members, members_step, sign_upload):



    with gr.Row():

        with gr.Column(visible=True):
            members_radio = gr.Radio(label='Member', info='Select member to edit', interactive=True)

            sign_file = gr.File(file_count='single', file_types=['.png', '.webp', '.svg', '.jpeg', '.jpg'], interactive=True, height=120, label='Upload Sign')
            sign_preview = gr.Image(visible=True, image_mode='RGBA', sources=['upload', 'clipboard'], type="pil", buttons=None, format='png', interactive=False, label='Preview', height='100%', elem_classes='sticky-image-small')

        with gr.Column():
            #gr.HTML("Please work on a larger screen or scroll down.")

            sign_save = gr.Gallery(visible=False, type='pil')

            sing_size = gr.Slider(minimum=50, maximum=150, step=1, value=100, label='Sign Size', interactive=True)

            with gr.Row():
                sing_x = gr.Slider(minimum=-100, maximum=100, step=1, value=0, label='X offset', interactive=True, min_width=50)
                sing_y = gr.Slider(minimum=-100, maximum=100, step=1, value=0, label='Y offset', interactive=True, min_width=50)


            remove_bg = gr.Checkbox(label='Remove Background', info='If sign image has background, you can use this.\nIt can Fix white image')
            apply_btn = gr.Button(value='Apply', interactive=False)
            #gr.HTML(value="If sign image has background, you can use this.")


            progress_checkbox = gr.CheckboxGroup(interactive=False, visible=True, choices=None, label='Progress', info='You must complete all signatures to proceed.')
            btn4 = gr.Button("Next", interactive=False)
            btn4.click(lambda: gr.Walkthrough(selected=5), outputs=walkthrough)


            for sign_option in [sing_x, sing_y, sing_size, remove_bg]:
                sign_option.change(fn=lambda x: gr.Button(interactive=True, variant='primary') if x else gr.Button(interactive=False, variant='secondary'), inputs=sign_file, outputs=apply_btn)




            progress_checkbox.change(inputs=[progress_checkbox, members], outputs=btn4, fn=lambda x, y: gr.Button(interactive=True, variant='primary') if len(list(set(x))) == len(y) else gr.Button(interactive=False, variant='secondary'))

            members_step.select(inputs=members, outputs=[members_radio, progress_checkbox],
                                            fn=lambda x: (gr.Radio(choices=x, value=x[0]), gr.CheckboxGroup(choices=x)))

            members_radio.select(outputs=[sign_file, apply_btn], fn=lambda : (gr.File(value=None), gr.Button(variant='secondary', interactive=False)))

            sign_file.upload(fn=sign_upload, inputs=[color_json, members, members_radio, sign_save, sign_file, sing_x, sing_y, sing_size, remove_bg, progress_checkbox], outputs=[apply_btn, sign_preview, sign_save, progress_checkbox, color_json])#여기
            sign_file.change(fn=lambda x: ((gr.Button(variant='primary', interactive=True), None) if x else (gr.Button(variant='secondary', interactive=False), gr.Image(value=None))), inputs=sign_file, outputs=[apply_btn, sign_preview])

            apply_btn.click(fn=sign_upload, inputs=[color_json, members, members_radio, sign_save, sign_file, sing_x, sing_y, sing_size, remove_bg, progress_checkbox], outputs=[apply_btn, sign_preview, sign_save, progress_checkbox, color_json])

            return sign_save