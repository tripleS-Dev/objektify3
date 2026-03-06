from typing import Dict, List

def season_select_change(seasons_select, color_json): # -> class_name
    return list(color_json['seasons'][seasons_select].keys())
