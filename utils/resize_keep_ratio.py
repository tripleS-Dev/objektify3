from PIL import Image

from PIL import Image


def resize_keep_ratio(
    img: Image.Image,
    target_height: int | None = None,
    target_width: int | None = None,
    scale: float | None = None,
) -> Image.Image:
    width, height = img.size

    specified = [
        target_width is not None,
        target_height is not None,
        scale is not None,
    ]

    if sum(specified) != 1:
        raise ValueError(
            "target_width, target_height, scale 중 정확히 하나만 지정하세요."
        )

    if scale is not None:
        if scale <= 0:
            raise ValueError("scale은 0보다 커야 합니다.")
        new_width = int(width * scale)
        new_height = int(height * scale)

    elif target_width is not None:
        if target_width <= 0:
            raise ValueError("target_width는 0보다 커야 합니다.")
        ratio = target_width / width
        new_width = target_width
        new_height = int(height * ratio)

    else:  # target_height is not None
        if target_height <= 0:
            raise ValueError("target_height는 0보다 커야 합니다.")
        ratio = target_height / height
        new_width = int(width * ratio)
        new_height = target_height

    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return resized_img