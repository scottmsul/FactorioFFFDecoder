import argparse
import numpy as np
#import factorio_text_generator
from downscale import downscaled_data, DOWNSCALE_MODES
from util import adjust_borders, get_image
from PIL import Image
#import wand.image

PIXELS_PER_BLOCK = 4

# secret 1: Vulcanus, x=-1, y=11, err=0
# secret 2: Bacchus, x=-1, y=11, err=0
# secret 3: Fulgora, x=-1, y=11, err=0
# secret 4: Aquilo, x=-1, y=11, err=0

START_BLOCK = 0
END_BLOCK = 0

def check_word(text, secret, downscale_mode, x_offset, y_offset, top, bottom, left, right):
    secret_image = Image.open(secret)
    factorio_image = get_image(x_offset, y_offset, secret_image.width, secret_image.height, text)
    factorio_image = adjust_borders(factorio_image, top, right, bottom, left)
    downscaled_size = (secret_image.width//4, secret_image.height//4)
    secret_downscaled = downscaled_data(secret_image, downscaled_size, downscale_mode)
    factorio_downscaled = downscaled_data(factorio_image, downscaled_size, downscale_mode)
    secret_data = np.asarray(secret_downscaled).astype(int)[:,START_BLOCK:,:3]
    factorio_data = np.asarray(factorio_downscaled).astype(int)[:,START_BLOCK:,:3]
    #err = (factorio_data-secret_data).sum(axis=2)
    err = np.square(factorio_data-secret_data).sum()
    #err = ((factorio_data-secret_data)!=0).sum()
    return err

def check_word_pixels(text, secret, downscale_mode, x_offset, y_offset, top, bottom, left, right):
    secret_image = Image.open(secret)
    factorio_image = get_image(x_offset, y_offset, secret_image.width, secret_image.height, text)
    factorio_image = adjust_borders(factorio_image, top, right, bottom, left)
    downscaled_size = (secret_image.width//4, secret_image.height//4)
    secret_downscaled = downscaled_data(secret_image, downscaled_size, downscale_mode)
    factorio_downscaled = downscaled_data(factorio_image, downscaled_size, downscale_mode)
    secret_data = np.asarray(secret_downscaled).astype(int)[:,START_BLOCK:,:3]
    factorio_data = np.asarray(factorio_downscaled).astype(int)[:,START_BLOCK:,:3]
    err = np.abs(factorio_data-secret_data).sum(axis=2)
    return err

if __name__=='__main__':
    parser = argparse.ArgumentParser(prog='Check Word', description='This python module checks the amount of error for a given text, secret, and image configuration.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--text', help='text to check', required=True)
    parser.add_argument('-s', '--secret', help='filename of secret pixelated image', required=True)
    parser.add_argument('-dm', '--downscale-mode', help='downscale mode', choices=list(DOWNSCALE_MODES.keys()), required=False, default='magick_windows')
    parser.add_argument('-x', '--x-offset', help='number of pixels to shift text in x-direction', type=int, default=0, required=False)
    parser.add_argument('-y', '--y-offset', help='number of pixels to shift text in y-direction', type=int, default=0, required=False)
    parser.add_argument('-pt', '--top', help='Number of pixels to pad/trim (positive/negative) bottom of text', type=int, default=0, required=False)
    parser.add_argument('-pb', '--bottom', help='Number of pixels to pad/trim (positive/negative) bottom of text', type=int, default=0, required=False)
    parser.add_argument('-pl', '--left', help='Number of pixels to pad/trim (positive/negative) left of text', type=int, default=0, required=False)
    parser.add_argument('-pr', '--right', help='Number of pixels to pad/trim (positive/negative) right of text', type=int, default=0, required=False)
    args = parser.parse_args()

    #clear_image_from_cache(args.text)
    #start_countdown()

    err = check_word(args.text, args.secret, args.downscale_mode, args.x_offset, args.y_offset, args.top, args.bottom, args.left, args.right)
    err_pixels = check_word_pixels(args.text, args.secret, args.downscale_mode, args.x_offset, args.y_offset, args.top, args.bottom, args.left, args.right)
    print('err by block:')
    print(err_pixels)
    print(f'total err: {err}')
