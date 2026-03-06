def group(color_json, group):
    color_json['name'] = group
    return color_json


    # color_json에는 있지만 class_names에는 없는 키 삭제
    for key in list(color_json.keys()):
        if key not in add_seasons:
            del color_json[key]

def members(color_json, members):
    if not color_json.get('members'):
        color_json['members'] = {}

    # color_json에는 있지만 class_names에는 없는 키 삭제
    for key in list(color_json['members'].keys()):
        if key not in members:
            del color_json['members'][key]


    for member in members:
        if not color_json['members'].get(member):
            color_json['members'][member] = {}

    return color_json