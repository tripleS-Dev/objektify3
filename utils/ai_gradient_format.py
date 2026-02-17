from PIL import Image


def resize_and_split(img: Image.Image):


    # 2) 좌표 기준으로 분할 (PIL crop: right, lower는 제외)
    # (0,0)~(75,1673)  => (left=0, upper=0, right=76, lower=1673)
    left_img = img.crop((0, 0, 76, 1673))

    # (76,0)~(1158,1673) => (left=76, upper=0, right=1158, lower=1673)
    right_img = img.crop((76, 0, 1158, 1673))

    return left_img, right_img


if __name__ == "__main__":
    resize_and_split(
        img
    )