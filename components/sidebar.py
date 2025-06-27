import gradio as gr
from PIL import Image

from generate.front import resize_round
from utils import get_kr_time


def add_message(history, message):
    print("raw message : ", message)
    krtime = get_kr_time()
    if not message.get('files', []) == []:
        resize_round(Image.open(message['files'][0]))[0].save(f'./cache/ai_inputs/objektify-{krtime}.png')
        history.append({"role": "user", "content": {"path": f'./cache/ai_inputs/objektify-{krtime}.png'}})  # (role, content)
    if not message.get('text', None) is None:
        history.append({"role": "user", "content": message["text"]})  # (role, content)
    print("raw history : "+str(history))
    return history, gr.MultimodalTextbox(value=None, interactive=False)


from ai import generate_by_language

def bot(history, response_type):
    print("bot :", str(history))

    text, success, img_name = generate_by_language(history)
    if success:
        history.append({"role": "assistant", "content": f"{img_name}",})
    else:
        history.append({"role": "assistant", "content": text.split("</think>")[1]})
        #history.append({"role": "assistant", "content": text.split("</think>")[1]})

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
            file_types=["image", "text"],
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