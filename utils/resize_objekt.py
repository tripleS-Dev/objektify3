from typing import Tuple
from PIL import Image

from utils import extend_right_edge_inpaint


def resize_objekt(base: Image.Image, size: Tuple[int, int], move: int=0):
    b_x, b_y = base.size
    t_x, t_y = size


    if t_y / t_x  >= b_y / b_x: # 가로일때
        #print('가로')

        r = t_y / b_y
        B_x = t_x / r

        a = round((b_x - B_x) / 2)

        # 타겟(px) 기준 move를 원본 이미지 좌표계로 변환
        move_in_base = round(move / r)
        x_start = a + move_in_base
        x_end = x_start + B_x
        y_start = 0
        y_end = b_y

        # 좌표가 이미지 범위 내에 있도록 제한 (clamp)
        x_start = max(0, min(x_start, b_x))
        x_end = max(x_start, min(x_end, b_x))
        y_start = max(0, min(y_start, b_y))
        y_end = max(y_start, min(y_end, b_y))

        base = base.crop((x_start, y_start, x_end, y_end))
        base = base.resize((round((x_end-x_start)*r), t_y), Image.Resampling.LANCZOS)


    else: # 세로일때
        r = t_x / b_x
        B_y = t_y / r

        a = round((b_y - B_y) / 2)

        # 타겟(px) 기준 move를 원본 이미지 좌표계로 변환
        move_in_base = round(move / r)

        x_start = 0 + move_in_base
        x_end = b_x
        y_start = a
        y_end = y_start + B_y

        base = base.crop((x_start, y_start, x_end, y_end))
        base = base.resize((round((x_end-x_start)*r), round((y_end-y_start)*r)), Image.Resampling.LANCZOS)

    if base.size[0] < t_x:
        if True:
            base = extend_right_edge_inpaint(base, t_x - base.size[0])
        else:
            blank = Image.new('RGBA', size, (255,0,0))
            blank.paste(base, (0,0))
            base = blank

    #base.show()
    return base
