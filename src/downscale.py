import cv2
import numpy as np
import os
import subprocess
import wand.image
from PIL import Image
from util import PIXELS_PER_BLOCK

RESAMPLING_METHOD = Image.Resampling.BOX

def downscaled_data(image, new_size, downscale_mode='PILLOW'):
    if downscale_mode not in DOWNSCALE_MODES:
        raise ValueError(f'Mode {downscale_mode} not found')
    downscale_method = DOWNSCALE_MODES[downscale_mode]
    return downscale_method(image, new_size)

def downscaled_data_magick_windows(image, new_size):
    save_dir = os.path.join('images', 'tmp')
    os.makedirs(save_dir, exist_ok=True)
    start_filepath = os.path.join(save_dir, 'downscale_start_tmp.png')
    end_filepath = os.path.join(save_dir, 'downscale_end_tmp.png')
    image.save(start_filepath)
    subprocess.run(['magick', start_filepath, '-scale', '25%', end_filepath])
    image2 = Image.open(end_filepath).convert('RGB')
    image_data = np.asarray(image2).astype(float)[:,:,:3]
    return image_data

def downscaled_data_magick_linux(image, new_size):
    save_dir = os.path.join('images', 'tmp')
    os.makedirs(save_dir, exist_ok=True)
    start_filepath = os.path.join(save_dir, 'downscale_start_tmp.png')
    end_filepath = os.path.join(save_dir, 'downscale_end_tmp.png')
    image.save(start_filepath)
    subprocess.run(['convert', '-scale', '25%', start_filepath, end_filepath])
    image2 = Image.open(end_filepath).convert('RGB')
    image_data = np.asarray(image2).astype(float)[:,:,:3]
    return image_data

def downscaled_data_wand(image, new_size):
    img = wand.image.Image.from_array(np.asarray(image))
    img.resize(width=new_size[0], height=new_size[1], filter='box')
    data = np.array(img)
    return data

def downscaled_data_pillow(image, new_size):
    downscaled = image.resize(new_size, resample=RESAMPLING_METHOD)
    data = np.asarray(downscaled).astype(float)[:,:,:3]
    return data

def downscaled_data_opencv(image, new_size):
    image = image.convert('RGB')
    data = np.asarray(image)[:,:,::-1].copy()
    data = cv2.resize(data, (new_size[0], new_size[1]), interpolation=cv2.INTER_AREA)
    data = data.astype(float)
    return data

def downscaled_data_custom(image, new_size):
    new_width = image.width // PIXELS_PER_BLOCK + int(image.width%PIXELS_PER_BLOCK>0)
    new_height = image.height // PIXELS_PER_BLOCK + int(image.height%PIXELS_PER_BLOCK>0)
    # repeating should always make width/height divisible by new_width/new_height and correctly weigh pixels on boundaries
    image_data = np.asarray(image).astype(float)[:,:,:3]
    image_data = image_data.repeat(new_height, axis=0).repeat(new_width, axis=1)
    result = np.zeros((new_height, new_width, 3))
    y_spacing = image_data.shape[0] // new_height
    x_spacing = image_data.shape[1] // new_width
    for y in range(new_height):
        for x in range(new_width):
            # WOAH! rounding down instead of rounding nearest gives ZERO error!!!
            #avg = np.round(image_data[old_y_start:old_y_end, old_x_start:old_x_end, :].mean(axis=(0,1)))
            avg = image_data[y_spacing*y:y_spacing*(y+1), x_spacing*x:x_spacing*(x+1), :].mean(axis=(0,1)).astype(int)
            result[y,x,:] = avg
    return result

DOWNSCALE_MODES = {
    'magick_windows': downscaled_data_magick_windows,
    'magick_linux': downscaled_data_magick_linux,
    'wand': downscaled_data_wand,
    'pillow': downscaled_data_pillow,
    'opencv': downscaled_data_opencv,
    'custom': downscaled_data_custom,
}
