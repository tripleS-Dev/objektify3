import gradio as gr

from utils import rgba_to_hex


def by_season_init(add_seasons, color_json):  # -> seasons_select, class_name, color_json
    if not color_json.get("seasons"):
        color_json["seasons"] = {}

    def season_to_key(season: str) -> str:
        # 마지막 / 만 제거
        if "/" in season:
            left, right = season.rsplit("/", 1)
            return left + right
        return season

    # 원문 -> 저장용 key
    season_map = {season: season_to_key(season) for season in add_seasons}
    season_keys = list(season_map.values())
    valid_keys = set(season_keys)

    # color_json에는 있지만 add_seasons에는 없는 키 삭제
    for key in list(color_json["seasons"].keys()):
        if key not in valid_keys:
            del color_json["seasons"][key]

    # 시즌별 데이터 생성/갱신
    for season in add_seasons:
        season_key = season_map[season]

        if season_key not in color_json["seasons"]:
            if season in color_json["seasons"]:
                color_json["seasons"][season_key] = color_json["seasons"].pop(season)
            else:
                color_json["seasons"][season_key] = {}

        # display는 원문 저장
        color_json["seasons"][season_key]["display"] = season

    return (
        gr.Radio(
            choices=season_keys,                         # <- 여기 변경
            value=season_keys[0] if season_keys else None
        ),
        gr.Dropdown(choices=None),
        color_json
    )


    return gr.Radio(choices=add_seasons, value=add_seasons[0]), gr.Dropdown(choices=None), color_json

def class_name_change(seasons_select, class_names, color_json, bc, tc):

    season_colors = color_json['seasons'][seasons_select]


    # color_json에는 있지만 class_names에는 없는 키 삭제
    for key in list(season_colors.keys()):
        if key not in class_names:
            if not key == "display":
                del season_colors[key]


    if not len(class_names) >= 1:
        return gr.Radio(choices=class_names, value=None), color_json




    # class_names에는 있지만 color_json에는 없는 키 추가
    for class_name in class_names:
        if class_name not in season_colors:
            season_colors[class_name] = [rgba_to_hex(bc), rgba_to_hex(tc)]

    return gr.Radio(choices=class_names, value=class_names[0]), color_json