from ai.comfyui_api.ai_gradient import run_gradient_ws_image
import gradio as gr

def make_ai_gradient(ai_color, ai_color_shape, seed):
    if ai_color == []:
        gr.Info('Please select at least one AI color.')
        return

    if ai_color_shape == 'Gradient':
        shape = 'wavy, '
    elif ai_color_shape == 'Wave':
        shape = 'wave, '
    else:
        shape = 'wavy'

    prompt = shape + ', '.join(ai_color) + ', gradient'

    print(prompt)

    img = run_gradient_ws_image(seed, prompt)



    return img