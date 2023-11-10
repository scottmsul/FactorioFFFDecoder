import numpy as np
from PIL import Image
import cv2
import hashlib
import os
import subprocess
import wand.image

PIXELS_PER_BLOCK = 4
RESAMPLING_METHOD = Image.Resampling.BOX
FACTORIO_BACKGROUND_COLOR = (36, 35, 36)
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

def downscaled_data(image, new_size):
    image.save('downscale_start_tmp.png')
    subprocess.run(['magick', 'downscale_start_tmp.png', '-scale', '25%', 'downscale_end_tmp.png'])
    #subprocess.run(['convert', '-scale', '25%', 'downscale_start_tmp.png', 'downscale_end_tmp.png'])
    image2 = Image.open('downscale_end_tmp.png').convert('RGB')
    image_data = np.asarray(image2).astype(float)[:,:,:3]
    return image_data

#def downscaled_data(image, new_size):
#    img = wand.image.Image.from_array(np.asarray(image))
#    img.resize(width=new_size[0], height=new_size[1], filter='box')
#    data = np.array(img)
#    return data

#def downscaled_data(image, new_size):
#    downscaled = image.resize(new_size, resample=RESAMPLING_METHOD)
#    data = np.asarray(downscaled).astype(float)[:,:,:3]
#    return data

#def downscaled_data(image, new_size):
#    image = image.convert('RGB')
#    data = np.asarray(image)[:,:,::-1].copy()
#    #data = cv2.resize(data, (new_size[0], new_size[1]), interpolation=cv2.INTER_LINEAR)
#    data = cv2.resize(data, (new_size[0], new_size[1]), interpolation=cv2.INTER_AREA)
#    #data = cv2.resize(data, (new_size[0], new_size[1]), interpolation=cv2.INTER_NEAREST)
#    data = data.astype(float)
#    return data

# def downscaled_data(image):
#     new_width = image.width // PIXELS_PER_BLOCK + int(image.width%PIXELS_PER_BLOCK>0)
#     new_height = image.height // PIXELS_PER_BLOCK + int(image.height%PIXELS_PER_BLOCK>0)
#     # repeating should always make width/height divisible by new_width/new_height and correctly weigh pixels on boundaries
#     image_data = np.asarray(image).astype(float)[:,:,:3]
#     image_data = image_data.repeat(new_height, axis=0).repeat(new_width, axis=1)
#     result = np.zeros((new_height, new_width, 3))
#     y_spacing = image_data.shape[0] // new_height
#     x_spacing = image_data.shape[1] // new_width
#     for y in range(new_height):
#         for x in range(new_width):
#             # WOAH! rounding down instead of rounding nearest gives ZERO error!!!
#             #avg = np.round(image_data[old_y_start:old_y_end, old_x_start:old_x_end, :].mean(axis=(0,1)))
#             avg = image_data[y_spacing*y:y_spacing*(y+1), x_spacing*x:x_spacing*(x+1), :].mean(axis=(0,1)).astype(int)
#             result[y,x,:] = avg
#     return result

# def downscaled_data(image):
#     new_width = image.width // PIXELS_PER_BLOCK + int(image.width%PIXELS_PER_BLOCK>0)
#     new_height = image.height // PIXELS_PER_BLOCK + int(image.height%PIXELS_PER_BLOCK>0)
#     # repeating should always make width/height divisible by new_width/new_height and correctly weigh pixels on boundaries
#     image_data = np.asarray(image).astype(float)[:,:,:3]
#     sum_result = np.zeros((new_height, new_width, 3))
#     count_result = np.zeros((new_height, new_width, 3))
#     for y in range(image.height):
#         for x in range(image.width):
#             result_y = int((new_height / image.height ) * y)
#             result_x = int((new_width / image.width ) * x)
#             sum_result[result_y, result_x] += image_data[y,x,:]
#             count_result[result_y, result_x,:] += 1
#     avg_result = (sum_result / count_result).astype(int)
#     return avg_result

# def downscaled_data(image):
#     # repeating should always make width/height divisible by four and correctly weigh pixels on boundaries
#     image_data = np.asarray(image).astype(float)[:,:,:3]
#
#     for y in range(new_height):
#         for x in range(new_width):
#             # WOAH! rounding down instead of rounding nearest gives ZERO error!!!
#             #avg = np.round(image_data[old_y_start:old_y_end, old_x_start:old_x_end, :].mean(axis=(0,1)))
#             avg = image_data[y_spacing*y:y_spacing*(y+1), x_spacing*x:x_spacing*(x+1), :].mean(axis=(0,1)).astype(int)
#             result[y,x,:] = avg
#     return result

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
