# copy/paste into gimp to compare w/ original Nauvis
# looks like TitilliumWeb-Regular with size 14 font matches exactly
import os
from PIL import Image, ImageDraw, ImageFont

IMAGE_NUM = 5
TEXT = 'Earthland'

IMAGE_FILENAME = os.path.join('images', 'secrets', f'secret{IMAGE_NUM}.png')
FONT = ImageFont.truetype("fonts/TitilliumWeb-Regular.ttf", 14)
X_LEFT_OFFSET = 0
Y_TOP_OFFSET = 15

with Image.open(IMAGE_FILENAME).convert('RGBA') as image:
    d = ImageDraw.Draw(image)
    d.text((X_LEFT_OFFSET, Y_TOP_OFFSET), font=FONT, text=TEXT, anchor='ls')
    image.save(os.path.join('images', 'overlay', f'overlay{IMAGE_NUM}_{TEXT}.png'))
