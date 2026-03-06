import gradio as gr


def class_select_select(seasons_select, class_select, color_json): # -> bc, tc
    if not class_select:
        return gr.ColorPicker(value='#FFFFFF'), gr.ColorPicker(value='#000000')

    bc = color_json['seasons'][seasons_select][class_select][0]
    tc = color_json['seasons'][seasons_select][class_select][1]
    return gr.ColorPicker(value=bc), gr.ColorPicker(value=tc)