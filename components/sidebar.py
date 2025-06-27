import gradio as gr
from PIL import Image

from generate.front import resize_round
from utils import get_kr_time


def add_message(history, message):
    print("raw message : ", message)

    history.append({"role": "user", "content": message["text"]})  # (role, content)
    print("raw history : "+str(history))
    return history, gr.MultimodalTextbox(value=None, interactive=False)


from ai import generate_by_language

def bot(history, response_type):
    print("bot :", str(history))

    text = generate_by_language(history)

    history.append({"role": "assistant", "content": text})

    print(history)
    return history


def sidebar(open=False):
    with gr.Sidebar(open=open) as side:
        chatbot = gr.Chatbot(
            elem_id="chatbot",
            bubble_full_width=False,
            scale=1,
            type='messages'
        )

        chat_input = gr.MultimodalTextbox(
            interactive=True,
            placeholder="Enter message or upload file...",
            show_label=False,
            file_types=["text"],
        )
        response_type = gr.Radio(
            [
                "image",
                "text",
                "gallery",
                "video",
                "audio",
                "html",
            ],
            value="text",
            label="Response Type",
            visible=False,
        )
        chat_msg = chat_input.submit(
            add_message, [chatbot, chat_input], [chatbot, chat_input]
        )
        bot_msg = chat_msg.then(
            bot, [chatbot, response_type], chatbot
        )
        bot_msg.then(lambda: gr.MultimodalTextbox(interactive=True), None, [chat_input])

    return side