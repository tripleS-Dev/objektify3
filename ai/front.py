from typing import Dict

from ollama import ChatResponse, chat
from pydash import retry

from generate.front import generate_front
from PIL import Image

from utils import get_kr_time


def make_card(input_image_path, name, group, background_color, text_color, number, alphabet, serial):
    data = {
        "artist": {
            "name": name,
            "group": group
        },
        "appearance": {
            "background_color": background_color,
            "text_color": text_color,
        },
        "identifiers": {
            "number": number,
            "alphabet": alphabet,
            "serial": serial
        }
    }
    krtime = get_kr_time()
    generated_img = generate_front(Image.open(input_image_path), data).save(f"./cache/ai_outputs/objektify-{krtime}.png")

    return generated_img




model_name = 'gemma3n'

def generate_by_language(historyR: list):
    from ai.system_prompt import system_prompt_no_tool

    history = historyR.copy()

    print("raw gen history : "+str(history))



    for i in range(len(history)):
        if history[i].get('role', None) == 'user':
            if not isinstance(history[i].get('content', None), str):
                history[i]['content'] = "input_image_path = " + history[i].get('content')[0].split("\\")[-1]


    messages = [{'role': 'system', 'content': system_prompt_no_tool}] + history


    response: ChatResponse = chat(
      model_name,
      messages=messages,
    )

    return response.message.content

if __name__ == '__main__':
    generate_by_language('서연 100')