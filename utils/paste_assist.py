from PIL import Image

def paste_correctly(blank: Image.Image, position: tuple[int, int], img: Image.Image):
    # overlay 크기만큼 빈 캔버스 하나 만들고 그 위에 그대로 paste
    tmp = Image.new("RGBA", blank.size, (0, 0, 0, 0))
    tmp.paste(img, position)  # 여기선 mask 옵션 X

    blank = Image.alpha_composite(blank, tmp)  # 올바른 Porter-Duff OVER 블렌드
    return blank