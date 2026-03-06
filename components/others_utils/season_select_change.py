from typing import Dict, List

def season_select_change(seasons_select, color_json):  # -> class_name
    season_data = color_json.get("seasons", {}).get(seasons_select, {})
    class_name = [key for key in season_data.keys() if key != "display"]
    return class_name
