import qrcode
from PIL import Image

def qr_image(url):
    # Generate QR code with a smaller border
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,  # Reduce the border by the border_reduction amount
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    qr_img = qr_img.resize((313,311), Image.Resampling.LANCZOS)

    return qr_img



if __name__ == '__main__':
    qr_image('hi').show()