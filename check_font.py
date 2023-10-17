
# copy/paste into gimp to compare w/ original Nauvis
# looks like TitilliumWeb-Regular with size 14 font matches exactly
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont

BLACK = (0, 0, 0, 255)
FACTORIO_BACKGROUND_COLOR = (36, 35, 36, 255)

reference_image = Image.open(os.path.join('images', 'reference', 'overview.png'))
reference_data = np.asarray(reference_image)[:,:,:3].sum(axis=2)

RESAMPLING_METHOD = Image.Resampling.BOX

font_size = 14
x_offset = 3
y_offset = reference_image.height - 4
fnt = ImageFont.truetype(os.path.join('fonts', 'TitilliumOTF', 'Titillium-Regular.otf'), 14)
# fnt = ImageFont.truetype(os.path.join('fonts', 'TitilliumTTF', 'TitilliumWeb-Regular.ttf'), 14)

img  = Image.new( mode="RGBA", size=reference_image.size , color=FACTORIO_BACKGROUND_COLOR)
d = ImageDraw.Draw(img)
d.text((x_offset, y_offset), "Overview", font=fnt, fill=(255, 255, 255, 255), anchor='ls')
img = img.convert('RGB')
img.save(os.path.join('images', 'reference', 'overview_guess.png'))
img_data = np.asarray(img)[:,:,:3].sum(axis=2)
#err = np.abs(reference_data-img_data).sum()
err = np.square(reference_data-img_data).sum()
print(f'err: {err}')
