import gradio as gr


def all_seasons_have_class(data: dict):
    seasons = data.get("seasons", {})

    if not isinstance(seasons, dict) or not seasons:
        return gr.Button(interactive=False, variant='secondary')

    for season_info in seasons.values():
        if not isinstance(season_info, dict):
            return gr.Button(interactive=False, variant='secondary')

        # display를 제외한 다른 키가 하나라도 있는지 확인
        if not any(key != "display" for key in season_info):
            return gr.Button(interactive=False, variant='secondary')

    return gr.Button(interactive=True, variant='primary')