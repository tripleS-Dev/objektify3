import gradio as gr
from html_elements import share_js, toggle_sidebar

def download_share_sidebar(raws, go_download_share):
    with gr.Sidebar(position='right', open=False) as download_bar:

        front_raw, back_raw, combined_raw = raws


        gr.HTML(value="""<div align="center"><h2><b>Download</b></h2></div>""")

        download_front = gr.DownloadButton(label='Front', variant="primary")
        download_back = gr.DownloadButton(label='Back', variant="primary")
        download_combine = gr.DownloadButton(label='Combined', variant="primary")
        download_buttons = [download_front, download_back, download_combine]

        gr.HTML(value="""<div align="center"><h2><b>Share</b></h2></div>""")


        share_front = gr.Button(value='Front', variant="primary")
        share_back = gr.Button(value='Back', variant="primary")
        share_combine = gr.Button(value='Combined', variant="primary")
        share_buttons = [share_front, share_back, share_combine]

        share_front.click(fn=None, inputs=front_raw, js=share_js, outputs=None)
        share_back.click(fn=None, inputs=back_raw, js=share_js, outputs=None)
        share_combine.click(fn=None, inputs=combined_raw, js=share_js, outputs=None)


        close = gr.Button(elem_id="bottom-btn", value='close')
        close.click(fn=None, inputs=[], outputs=[], js=toggle_sidebar)

        download_bar.collapse(fn=lambda : gr.Button(variant="primary"), outputs=go_download_share)
        download_bar.expand(fn=lambda : gr.Button(variant="secondary"), outputs=go_download_share)

    return download_bar, download_buttons + share_buttons