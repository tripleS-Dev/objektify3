from __future__ import annotations
from pathlib import Path
from typing import Union

import cv2
import numpy as np
from PIL import Image

ArrayLike = Union[str, Path, np.ndarray]


def _to_float01(a: np.ndarray) -> np.ndarray:
    if np.issubdtype(a.dtype, np.floating):
        out = a.astype(np.float32, copy=False)
        if out.max() > 1.5:
            out = out / 255.0
    else:
        out = a.astype(np.float32) / 255.0
    return np.clip(out, 0.0, 1.0)


def _imread_unicode(path: str | Path, flags: int = cv2.IMREAD_UNCHANGED) -> np.ndarray:
    """
    Windows 한글/유니코드 경로에서도 안전하게 이미지 읽기
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"파일이 존재하지 않습니다: {path}")

    try:
        data = np.fromfile(str(path), dtype=np.uint8)
    except Exception as e:
        raise FileNotFoundError(f"파일 읽기 실패: {path}") from e

    if data.size == 0:
        raise FileNotFoundError(f"파일을 읽었지만 내용이 비어 있습니다: {path}")

    arr = cv2.imdecode(data, flags)
    if arr is None:
        raise FileNotFoundError(f"이미지 디코딩 실패: {path}")

    return arr


def _imwrite_unicode(path: str | Path, image: np.ndarray) -> None:
    """
    Windows 한글/유니코드 경로에서도 안전하게 이미지 저장
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ext = path.suffix or ".png"
    ok, encoded = cv2.imencode(ext, image)
    if not ok:
        raise IOError(f"이미지 인코딩 실패: {path}")

    try:
        encoded.tofile(str(path))
    except Exception as e:
        raise IOError(f"이미지 저장 실패: {path}") from e

def pad_with_edge_median_color(img: np.ndarray, scale: float = 1.5) -> np.ndarray:
    """
    이미지의 가장자리 픽셀들의 중앙값 색상을 구해서,
    원본 크기의 scale배가 되도록 해당 색상으로 패딩합니다.

    Parameters
    ----------
    img : np.ndarray
        입력 이미지.
        - grayscale: (H, W)
        - color: (H, W, C)
    scale : float
        최종 출력 크기 배율. 기본값 1.5

    Returns
    -------
    np.ndarray
        패딩된 이미지 (numpy array)
    """
    if not isinstance(img, np.ndarray):
        raise TypeError("img must be a numpy.ndarray")
    if img.ndim not in (2, 3):
        raise ValueError("img must have shape (H, W) or (H, W, C)")
    if scale < 1.0:
        raise ValueError("scale must be >= 1.0")

    h, w = img.shape[:2]

    # 가장자리 마스크
    edge_mask = np.zeros((h, w), dtype=bool)
    edge_mask[0, :] = True
    edge_mask[-1, :] = True
    edge_mask[:, 0] = True
    edge_mask[:, -1] = True

    # 가장자리 픽셀 추출
    edge_pixels = img[edge_mask]  # grayscale: (N,), color: (N, C)

    # 중앙값 색상 계산
    median_color = np.median(edge_pixels, axis=0)

    # dtype 유지
    if np.issubdtype(img.dtype, np.integer):
        median_color = np.rint(median_color).astype(img.dtype)
    else:
        median_color = median_color.astype(img.dtype)

    # 목표 크기 계산
    new_h = int(np.ceil(h * scale))
    new_w = int(np.ceil(w * scale))

    pad_h = new_h - h
    pad_w = new_w - w

    top = pad_h // 2
    bottom = pad_h - top
    left = pad_w // 2
    right = pad_w - left

    # 패딩 이미지 생성
    if img.ndim == 2:
        out = np.full((new_h, new_w), median_color, dtype=img.dtype)
    else:
        c = img.shape[2]
        out = np.empty((new_h, new_w, c), dtype=img.dtype)
        out[...] = median_color

    # 원본 삽입
    out[top:top + h, left:left + w] = img

    return out

def _load_rgb_and_alpha(
    image: Union[str, Path, np.ndarray, Image.Image],
    input_order: str = "bgr",
    keep_existing_alpha: bool = True,
):
    # 1) PIL.Image.Image 입력 처리
    if isinstance(image, Image.Image):
        pil = image
        arr = np.array(pil)
    elif isinstance(image, (str, Path)):
        # 기존 cv2.imread -> 유니코드 안전 버전으로 교체
        arr = _imread_unicode(image, cv2.IMREAD_UNCHANGED)
        input_order = "bgra" if (arr.ndim == 3 and arr.shape[2] == 4) else "bgr"
    else:
        arr = np.asarray(image)

    arr = pad_with_edge_median_color(arr)

    if arr.ndim == 2:
        rgb = np.repeat(arr[..., None], 3, axis=2)
        alpha = None

    elif arr.ndim == 3 and arr.shape[2] == 3:
        order = input_order.lower()
        if order == "bgr":
            rgb = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB)
        elif order == "rgb":
            rgb = arr
        else:
            raise ValueError("3채널 ndarray는 input_order='bgr' 또는 'rgb' 여야 합니다.")
        alpha = None

    elif arr.ndim == 3 and arr.shape[2] == 4:
        order = input_order.lower()
        if order == "bgra":
            rgb = cv2.cvtColor(arr, cv2.COLOR_BGRA2RGB)
            alpha = arr[..., 3] if keep_existing_alpha else None
        elif order == "rgba":
            rgb = arr[..., :3]
            alpha = arr[..., 3] if keep_existing_alpha else None
        else:
            raise ValueError("4채널 ndarray는 input_order='bgra' 또는 'rgba' 여야 합니다.")

    else:
        raise ValueError("image는 경로, grayscale ndarray, 3채널 ndarray, 4채널 ndarray 중 하나여야 합니다.")

    rgb = _to_float01(rgb)
    alpha = _to_float01(alpha) if alpha is not None else None
    return rgb, alpha




def remove_signature_background(
    image: Union[str, Path, np.ndarray, Image.Image],
    *,
    input_order: str = "bgr",
    work_max_side: int = 512,
    bg_sigma_frac: float = 0.03,
    polarity: str = "auto",   # "auto" | "dark" | "light" | "both"
    alpha_gamma: float = 0.9,
    keep_existing_alpha: bool = True,
    despeckle: bool = True,
) -> Image.Image:
    """
    서명 이미지의 배경을 제거해 RGBA(uint8, RGB order)로 반환합니다.
    """

    rgb, src_alpha = _load_rgb_and_alpha(
        image,
        input_order=input_order,
        keep_existing_alpha=keep_existing_alpha,
    )
    h, w = rgb.shape[:2]

    scale = min(1.0, work_max_side / max(h, w))
    sw = max(1, int(round(w * scale)))
    sh = max(1, int(round(h * scale)))
    small = cv2.resize(rgb, (sw, sh), interpolation=cv2.INTER_AREA)

    sigma = max(3.0, max(sh, sw) * bg_sigma_frac)
    bg_small = cv2.GaussianBlur(
        small,
        ksize=(0, 0),
        sigmaX=sigma,
        sigmaY=sigma,
        borderType=cv2.BORDER_REPLICATE,
    )
    bg = cv2.resize(bg_small, (w, h), interpolation=cv2.INTER_LINEAR)

    dark_diff = np.max(bg - rgb, axis=2)
    light_diff = np.max(rgb - bg, axis=2)

    pol = polarity.lower()
    if pol == "auto":
        d_score = float(np.percentile(dark_diff, 99.8))
        l_score = float(np.percentile(light_diff, 99.8))
        if d_score > l_score * 1.25:
            diff = dark_diff
        elif l_score > d_score * 1.25:
            diff = light_diff
        else:
            diff = np.maximum(dark_diff, light_diff)
    elif pol == "dark":
        diff = dark_diff
    elif pol == "light":
        diff = light_diff
    elif pol == "both":
        diff = np.maximum(dark_diff, light_diff)
    else:
        raise ValueError("polarity는 'auto', 'dark', 'light', 'both' 중 하나여야 합니다.")

    diff = cv2.GaussianBlur(diff, (0, 0), sigmaX=0.8, sigmaY=0.8)

    diff_u8 = np.clip(diff * 255.0, 0, 255).astype(np.uint8)
    otsu_t, _ = cv2.threshold(diff_u8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    otsu_t = otsu_t / 255.0

    med = float(np.median(diff))
    mad = float(np.median(np.abs(diff - med))) + 1e-6
    noise_floor = med + 2.5 * 1.4826 * mad
    fg_ref = float(np.percentile(diff, 99.7))

    low = min(max(noise_floor, otsu_t * 0.35), fg_ref * 0.8)
    high = max(fg_ref, low + 1e-4)

    alpha = np.clip((diff - low) / (high - low), 0.0, 1.0)

    if alpha_gamma != 1.0:
        alpha = np.power(alpha, alpha_gamma)

    if src_alpha is not None:
        alpha *= src_alpha

    if despeckle:
        mask = (alpha > 0.03).astype(np.uint8)
        n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
        if n > 1:
            min_area = max(4, int(h * w * 1e-5))
            keep = np.zeros(n, dtype=np.uint8)
            keep[stats[:, cv2.CC_STAT_AREA] >= min_area] = 1
            keep[0] = 0
            alpha *= keep[labels]

    safe_alpha = np.clip(alpha[..., None], 1e-3, 1.0)
    fg_rgb = bg + (rgb - bg) / safe_alpha
    fg_rgb = np.clip(fg_rgb, 0.0, 1.0)

    fg_rgb[alpha < (1.0 / 255.0)] = 0.0

    rgba = np.dstack([fg_rgb, alpha])
    rgba_u8 = np.clip(rgba * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(rgba_u8, mode="RGBA")


def save_transparent_png(src: ArrayLike, dst_png: str | Path, **kwargs) -> np.ndarray:
    """
    입력 이미지를 투명 PNG로 저장하고 RGBA 배열도 반환합니다.
    """
    rgba_img = remove_signature_background(src, **kwargs)

    # PIL.Image -> numpy.ndarray 로 변환
    rgba = np.asarray(rgba_img, dtype=np.uint8)

    # 기존 cv2.imwrite -> 유니코드 안전 저장
    bgra = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)
    _imwrite_unicode(dst_png, bgra)

    return rgba


if __name__ == "__main__":
    rgba_img = remove_signature_background("signature.png")
    rgba = np.asarray(rgba_img, dtype=np.uint8)
    bgra = cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)
    _imwrite_unicode("signature_transparent.png", bgra)