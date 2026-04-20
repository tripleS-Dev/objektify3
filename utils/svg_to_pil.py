from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional, Union

from PIL import Image
import cairosvg


def svg_to_pil(
    svg_path: Union[str, Path],
    target_width: Optional[int] = None,
    target_height: Optional[int] = None,
) -> Image.Image:
    """
    SVG 파일 경로를 받아 비율을 유지한 PIL Image 객체로 변환한다.

    Args:
        svg_path: SVG 파일 경로
        target_width: 목표 너비 (target_height와 동시에 지정 불가)
        target_height: 목표 높이 (target_width와 동시에 지정 불가)

    Returns:
        PIL.Image.Image 객체

    Raises:
        ValueError: target_width, target_height 지정 규칙이 맞지 않을 때
        FileNotFoundError: SVG 파일이 없을 때
    """
    svg_path = Path(svg_path)

    if not svg_path.is_file():
        raise FileNotFoundError(f"SVG 파일을 찾을 수 없습니다: {svg_path}")

    # 둘 중 정확히 하나만 입력
    if (target_width is None) == (target_height is None):
        raise ValueError("target_width와 target_height 중 정확히 하나만 입력해야 합니다.")

    if target_width is not None and target_width <= 0:
        raise ValueError("target_width는 0보다 큰 정수여야 합니다.")

    if target_height is not None and target_height <= 0:
        raise ValueError("target_height는 0보다 큰 정수여야 합니다.")

    svg_bytes = svg_path.read_bytes()

    render_kwargs = {}
    if target_width is not None:
        render_kwargs["output_width"] = int(target_width)
    else:
        render_kwargs["output_height"] = int(target_height)

    png_bytes = cairosvg.svg2png(
        bytestring=svg_bytes,
        **render_kwargs,
    )

    image = Image.open(BytesIO(png_bytes))
    image.load()  # BytesIO와 분리해서 안전하게 반환
    return image