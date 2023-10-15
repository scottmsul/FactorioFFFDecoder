# copy/paste into gimp to compare w/ original Nauvis
# looks like TitilliumWeb-Regular with size 14 font matches exactly
from PIL import Image, ImageDraw, ImageFont

width = 400
height = 300

# may need light
fnt = ImageFont.truetype("fonts/TitilliumWeb-Regular.ttf", 14)

img  = Image.new( mode = "RGB", size = (width, height) )
d = ImageDraw.Draw(img)
d.text((1, 1), "Ykwamxi", font=fnt, fill=(255, 255, 255, 128))

img.save('test.png')
