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



    return "Success", True, f"objektify-{krtime}.png"



# Tools can still be manually defined and passed into chat
make_card_tool = {
    "type": "function",
    "function": {
        "name": "make front card",
        "description": "make front card",
        "parameters": {
            "type": "object",

            # 1️⃣ keep only the fields that must always be present
            "required": ['name', 'group', 'background_color', 'text_color', 'number', 'alphabet', 'serial', 'input_image_path'],

            "properties": {
                "input_image_path": {
                    "type": "string",
                    "description": "name of the user input image",
                },

                "name": {
                    "type": "string",
                    "description": "The name of the card"
                },
                "group": {
                    "type": "string",
                    "description": "The group the card belongs to"
                },
                "background_color": {
                    "type": "string",
                    "description":
                        "The background (label) color of the card. Must be hex and start with #"
                },
                "text_color": {
                    "type": "string",
                    "description":
                        "The text color of the card. Must be hex and start with #"
                },

                # 2️⃣ each of these may be an int / string *or* null
                "number": {
                    "type": "string",
                    "description": "The number associated with the card"
                },
                "alphabet": {
                    "type": "string",
                    "description": "The alphabet character for the card"
                },
                "serial": {
                    "type": "string",
                    "description": "The serial number of the card. ex) 1"
                }
            }
        }
    }
}

model_name = 'qwen3:30b-a3b'

def generate_by_language(historyR: list):
    from ai.system_prompt import system_prompt_eng

    history = historyR.copy()

    print("raw gen history : "+str(history))



    for i in range(len(history)):
        if history[i].get('role', None) == 'user':
            if not isinstance(history[i].get('content', None), str):
                history[i]['content'] = "input_image_path = " + history[i].get('content')[0].split("\\")[-1]


    messages = [{'role': 'system', 'content': system_prompt_eng}] + history
    #print('Prompt:', messages[0]['content'])

    available_functions = {
      'make_card': make_card,
    }

    response: ChatResponse = chat(
      model_name,
      messages=messages,
      tools=[make_card],
    )

    if response.message.tool_calls:
      # There may be multiple tool calls in the response
      for tool in response.message.tool_calls:
        # Ensure the function is available, and then call it
        if function_to_call := available_functions.get(tool.function.name):
          print('Calling function:', tool.function.name)
          print('Arguments:', tool.function.arguments)
          output = function_to_call(**tool.function.arguments)
          print('Function output:', output)
        else:
          print('Function', tool.function.name, 'not found')

    # Only needed to chat with the model using the tool call results
    if response.message.tool_calls:
      # Add the function response to messages for the model to use
      messages.append(response.message)
      messages.append({'role': 'tool', 'content': str(output[0]), 'name': tool.function.name})

      # Get final response from model with function outputs
      final_response = chat(model_name, messages=messages)
      print('Final response:', final_response.message.content)
      return final_response.message.content, True, output[2]
    else:
      print('No tool calls returned from model')
      print(response.message.content)
      return response.message.content, False, None

if __name__ == '__main__':
    generate_by_language('서연 100')