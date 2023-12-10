import numpy as np
from PIL import Image
import hashlib
import os
import subprocess

PIXELS_PER_BLOCK = 4
#FACTORIO_BACKGROUND_COLOR = (36, 35, 36)
FACTORIO_BACKGROUND_COLOR = (40, 39, 40)
TEXT_BOX_2_Y_OFFSET = 11 # number of pixels from top of text_box_2 that bottom of matches text line bottom

cache_dir = os.path.join('images', 'cache')

def get_filepath(text):
    os.makedirs(cache_dir, exist_ok=True)
    hashed = hashlib.sha256(str.encode(text)).hexdigest()
    filename = f'{hashed}.png'
    return os.path.abspath(os.path.join(cache_dir, filename))

def get_image(x_offset=0, y_offset=11, width=60, height=16, text='', use_cache=True):
    filepath = get_filepath(text)
    raw_img = Image.open(filepath)

    if x_offset > 0:
        raw_img = add_margin(raw_img, 0, 0, 0, x_offset, FACTORIO_BACKGROUND_COLOR)
    elif x_offset < 0:
        raw_img = raw_img.crop((-x_offset, 0, raw_img.width, raw_img.height))

    y_shift = y_offset - TEXT_BOX_2_Y_OFFSET
    if y_shift > 0:
        raw_img = add_margin(raw_img, y_shift, 0, 0, 0, FACTORIO_BACKGROUND_COLOR)
    elif y_shift < 0:
        raw_img = raw_img.crop((0, -y_shift, raw_img.width, raw_img.height))

    img = raw_img.crop((0, 0, width, height))
    return img

def get_filepath(text):
    os.makedirs(cache_dir, exist_ok=True)
    hashed = hashlib.sha256(str.encode(text)).hexdigest()
    filename = f'{hashed}.png'
    return os.path.abspath(os.path.join(cache_dir, filename))

def crop_width(image):
    min_x = image.width
    max_x = -1
    image_data = np.asarray(image)[:,:,:3]

    for i in range(image.height):
        for j in range(image.width):
            pixel = image_data[i,j,:]
            if (pixel != FACTORIO_BACKGROUND_COLOR).any():
                min_x = min(j, min_x)
                max_x = max(j, max_x)

    if min_x == image.width:
        min_x = 0
    if max_x == -1:
        max_x = image.width
    cropped_image = image.crop((min_x, 0, max_x+1, image.height))
    return cropped_image

def adjust_borders(image, top, right, bottom, left, color=FACTORIO_BACKGROUND_COLOR):
    # imagine the bottom-left of the image at the origin of a cartesian coordinate system
    # each argument shifts the image boundary by x pixels, where up/right are positive
    if top>0:
        image = add_margin(image, top, 0, 0, 0)
    elif top<0:
        image = image.crop((0, -top, image.width, image.height))

    if right>0:
        image = add_margin(image, 0, right, 0, 0)
    elif right<0:
        image = image.crop((0, 0, image.width+right, image.height))

    if bottom>0:
        image = add_margin(image, 0, 0, bottom, 0)
    elif bottom<0:
        image = image.crop((0, 0, image.width, image.height+bottom))

    if left>0:
        image = add_margin(image, 0, 0, 0, left)
    elif left<0:
        image = image.crop((-left, 0, image.width, image.height))

    return image

# copied from here: https://note.nkmk.me/en/python-pillow-add-margin-expand-canvas/
def add_margin(pil_img, top, right, bottom, left, color=FACTORIO_BACKGROUND_COLOR):
    width, height = pil_img.size
    new_width = width + right + left
    new_height = height + top + bottom
    result = Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result

# https://docs.wand-py.org/en/0.6.6/wand/image.html?highlight=extent#wand.image.BaseImage.extent
def add_margin_wand(wand_img, top, right, bottom, left):
    width, height = wand_img.width, wand_img.height
    new_width = width + right + left
    new_height = height + top + bottom
    wand_img_clone = wand_img.clone()
    wand_img_clone.extent(new_width, new_height, left, bottom)
    return wand_img_clone
