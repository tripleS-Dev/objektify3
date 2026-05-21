from PIL import Image
import numpy as np
import cv2

def extend_right_edge(img: Image.Image, extra_width: int = 118) -> Image.Image:
    # 원본 크기
    w, h = img.size

    # 우측 가장자리 1px 열 잘라내기
    right_edge = img.crop((w - 1, 0, w, h))  # (left, upper, right, lower)

    # 그 1px 열을 가로로 extra_width 만큼 늘리기
    stretched_edge = right_edge.resize((extra_width, h))

    # 새 캔버스 생성
    new_img = Image.new(img.mode, (w + extra_width, h))

    # 원본 붙이기
    new_img.paste(img, (0, 0))

    # 늘린 우측 가장자리 붙이기
    new_img.paste(stretched_edge, (w, 0))

    return new_img


def extend_right_edge_inpaint(
    img: Image.Image,
    extra_width: int = 32,
    radius: float = 3.0,
    method: int = cv2.INPAINT_TELEA,
) -> Image.Image:
    """
    오른쪽으로 extra_width 만큼 확장한 뒤,
    새로 생긴 우측 영역을 OpenCV inpaint로 채운다.

    지원 모드:
      - L
      - RGB
      - RGBA  (alpha는 마지막 열 복제로 확장)
    그 외 모드는 RGB로 변환 후 처리.
    """
    if extra_width <= 0:
        return img.copy()

    mode = img.mode
    if mode not in ("L", "RGB", "RGBA"):
        img = img.convert("RGB")
        mode = "RGB"

    arr = np.asarray(img)

    if mode == "RGBA":
        rgb = arr[..., :3]
        alpha = arr[..., 3]

        rgb_out = _extend_right_edge_inpaint_np(
            rgb, extra_width=extra_width, radius=radius, method=method
        )

        # alpha는 인페인팅보다 마지막 열 복제가 보통 더 안전함
        alpha_pad = np.repeat(alpha[:, -1:], extra_width, axis=1)
        alpha_out = np.concatenate([alpha, alpha_pad], axis=1)

        out = np.dstack([rgb_out, alpha_out])
        return Image.fromarray(out, mode="RGBA")

    out = _extend_right_edge_inpaint_np(
        arr, extra_width=extra_width, radius=radius, method=method
    )
    return Image.fromarray(out, mode=mode)


def _extend_right_edge_inpaint_np(
    arr: np.ndarray,
    extra_width: int,
    radius: float,
    method: int,
) -> np.ndarray:
    h, w = arr.shape[:2]

    # 확장 캔버스 생성
    if arr.ndim == 2:  # grayscale
        canvas = np.empty((h, w + extra_width), dtype=arr.dtype)
        canvas[:, :w] = arr
        canvas[:, w:] = arr[:, -1:]   # 초기값: 마지막 열 복제
    else:  # color
        c = arr.shape[2]
        canvas = np.empty((h, w + extra_width, c), dtype=arr.dtype)
        canvas[:, :w, :] = arr
        canvas[:, w:, :] = arr[:, -1:, :]  # 초기값: 마지막 열 복제

    # 새로 생긴 우측 영역만 inpaint 대상으로 지정
    mask = np.zeros((h, w + extra_width), dtype=np.uint8)
    mask[:, w:] = 255

    # inpaint
    out = cv2.inpaint(canvas, mask, radius, method)
    return out