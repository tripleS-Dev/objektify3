from PIL import Image

def crop_transparent_padding(img: Image.Image) -> Image.Image:
    """
    RGBA PIL 이미지에서 가장자리의 완전 투명한 패딩을 제거해서 반환.

    - 입력 이미지가 RGBA가 아니면 RGBA로 변환
    - 전부 투명한 이미지면 원본 크기의 빈 RGBA 이미지를 반환
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    alpha = img.getchannel("A")
    bbox = alpha.getbbox()

    if bbox is None:
        # 전체가 투명한 경우
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))

    return img.crop(bbox)