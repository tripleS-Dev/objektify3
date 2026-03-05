import gradio as gr


def by_season_init(add_seasons, ): # -> seasons_select, class_name, color_json

    color_json = {}

    for season in add_seasons:
        color_json[season] = {}


    return gr.Radio(choices=add_seasons, value=add_seasons[0]), gr.Dropdown(choices=None), color_json