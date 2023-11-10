import argparse
import numpy as np
from downscale import downscaled_data, DOWNSCALE_MODES
from factorio_text_generator import clear_image_from_cache, start_countdown, get_image, check_if_cached, display_message
from util import adjust_borders
from PIL import Image

def check_word(text, secret, downscale_mode, blocks, x_offset, y_offset, top, bottom, left, right):
    err = check_word_pixels(text, secret, downscale_mode, blocks, x_offset, y_offset, top, bottom, left, right)
    return err.sum()

def check_word_pixels(text, secret, downscale_mode, blocks, x_offset, y_offset, top, bottom, left, right):
    secret_image = Image.open(secret)
    factorio_image = get_image(x_offset, y_offset, secret_image.width, secret_image.height, text)
    factorio_image = adjust_borders(factorio_image, top, right, bottom, left)
    downscaled_size = (secret_image.width//4, secret_image.height//4)
    blocks = downscaled_size[0] if blocks == 0 else blocks
    secret_downscaled = downscaled_data(secret_image, downscaled_size, downscale_mode)
    factorio_downscaled = downscaled_data(factorio_image, downscaled_size, downscale_mode)
    secret_data = np.asarray(secret_downscaled).astype(int)[:,:blocks,:3]
    factorio_data = np.asarray(factorio_downscaled).astype(int)[:,:blocks,:3]
    err = np.square(factorio_data-secret_data).sum(axis=2)
    return err

HELP_DESCRIPTION = '''
This python module checks the amount of error for a given text, secret, and image configuration.

The following args give zero error, which use the 'custom' hand-written downscale method, although magick_linux also produces zero error.
> python .\src\check_word.py -t Vulcanus -s .\images\secrets\secret1.png -x -1 -y 11
> python .\src\check_word.py -t Bacchus -s .\images\secrets\secret2.png -x -1 -y 11
> python .\src\check_word.py -t Fulgora -s .\images\secrets\secret3.png -x -1 -y 11
> python .\src\check_word.py -t Aquilo -s .\images\secrets\secret4.png -x -1 -y 11
'''

if __name__=='__main__':
    parser = argparse.ArgumentParser(prog='Check Word', description=HELP_DESCRIPTION, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-t', '--text', help='text to check', required=True)
    parser.add_argument('-s', '--secret', help='filename of secret pixelated image', required=True)
    parser.add_argument('-dm', '--downscale-mode', help='downscale mode', choices=list(DOWNSCALE_MODES.keys()), required=False, default='custom')
    parser.add_argument('-b', '--blocks', help='number of horizontal blocks to check starting from the left, checks all blocks if None', required=False, type=int, default=0)
    parser.add_argument('-x', '--x-offset', help='number of pixels to shift text in x-direction', type=int, default=0, required=False)
    parser.add_argument('-y', '--y-offset', help='number of pixels to shift text in y-direction', type=int, default=0, required=False)
    parser.add_argument('-pt', '--top', help='Number of pixels to pad/trim (positive/negative) bottom of text', type=int, default=0, required=False)
    parser.add_argument('-pb', '--bottom', help='Number of pixels to pad/trim (positive/negative) bottom of text', type=int, default=0, required=False)
    parser.add_argument('-pl', '--left', help='Number of pixels to pad/trim (positive/negative) left of text', type=int, default=0, required=False)
    parser.add_argument('-pr', '--right', help='Number of pixels to pad/trim (positive/negative) right of text', type=int, default=0, required=False)
    parser.add_argument('-cc', '--clear-cache', help='If present, clear this word from the cache', required=False, action='store_true')
    args = parser.parse_args()

    if args.clear_cache:
        clear_image_from_cache(args.text)

    cached = check_if_cached(args.text)
    if not cached:
        start_countdown()

    err = check_word(args.text, args.secret, args.downscale_mode, args.blocks, args.x_offset, args.y_offset, args.top, args.bottom, args.left, args.right)
    err_pixels = check_word_pixels(args.text, args.secret, args.downscale_mode, args.blocks, args.x_offset, args.y_offset, args.top, args.bottom, args.left, args.right)
    print('err by block:')
    print(err_pixels)
    print(f'total err: {err}')

    if not cached:
        display_message('done!')
