from PIL import Image
import numpy as np

def color_change(img: Image.Image, new_hex: str) -> Image.Image:
    """
    img      : RGBA Pillow 이미지 객체
    new_rgb  : (R, G, B) 0–255 정수 3-튜플
    반환값   : 알파는 유지하고 RGB만 new_rgb로 바꾼 새 RGBA 이미지
    """
    # Pillow → NumPy 배열 (복사본을 만들어 원본은 건드리지 않음)
    arr = np.asarray(img.convert("RGBA")).copy()

    # 앞의 3채널(R,G,B)을 새 색으로 통째로 덮어쓰기
    new_hex = new_hex.lstrip('#')
    if len(new_hex) == 3:
        new_hex = ''.join([c * 2 for c in new_hex])
    r = int(new_hex[0:2], 16)
    g = int(new_hex[2:4], 16)
    b = int(new_hex[4:6], 16)
    new_rgb = (r, g, b)
    arr[..., :3] = new_rgb

    # NumPy 배열 → Pillow 이미지
    return Image.fromarray(arr, mode="RGBA")
