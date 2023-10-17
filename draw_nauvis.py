# copy/paste into gimp to compare w/ original Nauvis
# looks like TitilliumWeb-Regular with size 14 font matches exactly
import os
from PIL import Image, ImageDraw, ImageFont

RESAMPLING_METHOD = Image.Resampling.BOX

width = 400
height = 300

scale = 2

def downscale(image):
    new_width = image.width // scale
    new_height = image.height // scale
    downscaled = image.resize((new_width,new_height), resample=RESAMPLING_METHOD)
    return downscaled

# may need light
fnt = ImageFont.truetype("fonts/TitilliumWeb-Regular.ttf", 14.5)

FACTORIO_BACKGROUND_COLOR = (36, 35, 36)
img  = Image.new( mode = "RGB", size = (width, height) , color=FACTORIO_BACKGROUND_COLOR)
d = ImageDraw.Draw(img)
d.fontmode = 'I'
d.text((0.5, 1), "Overview", font=fnt, fill=(255, 255, 255, 255))

#img = downscale(img)

img.save(os.path.join('images', 'Nauvis.png'))
