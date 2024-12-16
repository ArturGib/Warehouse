from pyzbar.pyzbar import decode
from PIL import Image


def qr_data():
	qr_data = decode(Image.open("photo.png"))
	return str(qr_data[0][0])[2:-1]