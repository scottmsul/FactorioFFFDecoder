'''
This is the main brute-forcing script in the codebase.
No parse args, all settings are defined using variables at the top of the script.
Essentially this script works by checking one vertical block group at a time in the secret image.
Each "block" is a 4x4 pixel group in the secret image.
Suppose our secret had these blocks:

S11 S12 S13 S14
S21 S22 S23 S24
S31 S32 S33 S34

We generate a test string, eg the letter "A", then run it through the downscaling algorithm.
This generates a set of blocks we can compare to the secret:

T11 T12 T13 T14
T21 T22 T23 T24
T31 T32 T33 T34

At first we only compare the three left-most blocks.
The error is computed by summing (each pixel diff)^2, so (S11-T11)^2 + (S21-T21)^2 + (S31-T31)^2.
We then recursively add more letters, eg "Aa", "Ab", and so on.
If the additional letter doesn't change the left most downscaled block group, we prune that branch and return early.
If it does change, we add it and search another level recursively.
eg since "I" is a thin letter, we would also search "Ia" (keep), "Iaa" (prune), "Iab" (prune), etc.

Eventually we build up a list of the every possible letter combination that affects the first vertical block group.
We then take the N best combinations (defined in the variable RETAINED_GUESSES),
and use them as the starting points for the next vertical block group.
This lets the algorithm run in constant(ish) time.

There are two main modes: 'Factorio' and 'Pillow'.
Factorio uses the factorio_text_generator module to obtain images from a running Factorio instance,
    while Pillow uses Python's Pillow library to draw text from Factorio's font on Factorio's background color.
The Factorio method reproduces pixels perfectly but is really slow, while Pillow introduces some error but is really fast.
The Pillow method should not be overlooked, as it was able to discover the first four planet names despite having some error.
'''
import numpy as np
import os
import pandas as pd
import pprint
import string
from PIL import Image, ImageFont, ImageDraw
root_dir = os.path.realpath(os.path.join(__file__, '..', '..'))

from factorio_text_generator import get_image, display_message, start_countdown
from downscale import downscaled_data
from util import add_margin, PIXELS_PER_BLOCK, FACTORIO_BACKGROUND_COLOR

#Factorio is more accurate but slower
#METHOD = 'Factorio'
METHOD = 'Pillow'

if METHOD == 'Factorio':
    start_countdown()

IMAGE_NUM = 1
RETAINED_GUESSES = 10

# used to set the downscaling algorithm, see downscale.py for a full list of options
DOWNSCALE_MODE = 'magick_windows'

# used to prune when an error seems too high, this can be set to 1e99 to get the best group regardless of error
#MAX_ERROR = 5000
MAX_ERROR = 1e99

# used to control character sequence search space
def get_next_allowed_chars(text):
    next_allowed_chars = string.ascii_uppercase if text == '' else string.ascii_lowercase

    # ignore letters that would enter fourth block if secret is only three blocks tall
    global HEIGHT_BLOCKS
    if HEIGHT_BLOCKS==3:
        next_allowed_chars = next_allowed_chars.replace('g', '').replace('j', '').replace('p', '').replace('q', '').replace('y', '')

    return next_allowed_chars

# used to control how many blocks to check before halting, eg this lets us just check the first letter, or None to check all letters
#NUM_BLOCKS = 1
NUM_BLOCKS = None

# secrets 1, 2, 3, 4 all prefer (-1, 11)
X_LEFT_OFFSETS = [-1]
Y_TOP_OFFSETS = [11]
X_MARGINS = [0]
Y_MARGINS = [0]
HEIGHT_DELTAS = [0]
WIDTH_DELTAS = [0]

# my typical search space when I'm not sure
# X_LEFT_OFFSETS = [-2, -1, 0, 1, 2]
# Y_TOP_OFFSETS = [10, 11, 12, 13]
# X_MARGINS = [0]
# WIDTH_DELTAS = [-2, -1, 0, 1]
# Y_MARGINS = [0]
# HEIGHT_DELTAS = [-2, -1, 0, 1]

#### ONLY CHANGE STUFF ABOVE THIS LINE UNLESS YOU KNOW WHAT YOU'RE DOING ####

# hacky global variables
BLOCK = None
X_LEFT_OFFSET = None
Y_TOP_OFFSET = None
X_MARGIN = None
Y_MARGIN = None
WIDTH_DELTA = None
HEIGHT_DELTA = None

FONT = ImageFont.truetype("fonts/TitilliumTTF/TitilliumWeb-Regular.ttf", 14)

IMAGE_FILENAME = os.path.join(root_dir, 'images', 'secrets', f'secret{IMAGE_NUM}.png')
challenge_image = Image.open(IMAGE_FILENAME).convert('RGB')
downscaled_size = (challenge_image.width//4, challenge_image.height//4)
challenge_data = np.asarray(challenge_image)[::PIXELS_PER_BLOCK, ::PIXELS_PER_BLOCK, :3].astype(int)

challenge_width = challenge_image.width
WIDTH_BLOCKS = challenge_width // PIXELS_PER_BLOCK
ENDING_BLOCK = WIDTH_BLOCKS - 1
if NUM_BLOCKS is None:
    NUM_BLOCKS = WIDTH_BLOCKS

HEIGHT_PIXELS = challenge_image.height
HEIGHT_BLOCKS = HEIGHT_PIXELS//PIXELS_PER_BLOCK

def generate_image_from_text(width, text):
    if METHOD == 'Factorio':
        # method 1 - more accurate but slower (gets text from running Factorio instance)
        if text=='':
            img  = Image.new( mode = "RGB", size = (width, HEIGHT_PIXELS), color=FACTORIO_BACKGROUND_COLOR)
        else:
            img = get_image(X_LEFT_OFFSET, Y_TOP_OFFSET, width, HEIGHT_PIXELS, text)
    else:
        # method 2 - less accurate but faster (gets text from Pillow)
        img  = Image.new( mode = "RGB", size = (width, HEIGHT_PIXELS), color=FACTORIO_BACKGROUND_COLOR)
        d = ImageDraw.Draw(img)
        d.text((X_LEFT_OFFSET, Y_TOP_OFFSET), font=FONT, text=text, anchor='ls')

    # margins add extra blank lines
    # needed if the devs cut out pixels when copying then added blank lines when pixelating
    if X_MARGIN is not None and X_MARGIN!=0:
        img = add_margin(img, 0, 0, 0, X_MARGIN, FACTORIO_BACKGROUND_COLOR)
        img = img.crop((0, 0, img.width-X_MARGIN, img.height))
    if Y_MARGIN is not None and Y_MARGIN!=0:
        img = add_margin(img, 0, 0, Y_MARGIN, 0, FACTORIO_BACKGROUND_COLOR)
        img = img.crop((0, Y_MARGIN, img.width, img.height))
    # x_trims and y_trims cause the image to no longer evenly divide into blocks
    if WIDTH_DELTA > 0:
        img = add_margin(img, 0, WIDTH_DELTA, 0, 0)
    elif WIDTH_DELTA < 0:
        img = img.crop((0, 0, img.width+WIDTH_DELTA, img.height))
    if HEIGHT_DELTA > 0:
        img = add_margin(img, HEIGHT_DELTA, 0, 0, 0)
    elif HEIGHT_DELTA < 0:
        img = img.crop((0, -HEIGHT_DELTA, img.width, img.height))

    return img

def get_error(guess):
    curr_img = generate_image_from_text(challenge_width, guess)
    curr_downscaled_data = downscaled_data(curr_img, downscaled_size, DOWNSCALE_MODE)
    err = np.square(challenge_data-curr_downscaled_data).sum()
    #err = np.abs(challenge_image-curr_pixelated).sum()
    return err

# block num is how many blocks to the right we are
def get_block_charset(curr_num_blocks, curr_text, prev_img_downscaled_data=None):
    curr_img = generate_image_from_text(challenge_image.width+PIXELS_PER_BLOCK, curr_text)
    curr_img_downscaled_data = downscaled_data(curr_img, downscaled_size, DOWNSCALE_MODE)

    # if adding the new letter doesn't change the block data, don't include in the charset
    if (prev_img_downscaled_data is not None):
        diff = np.square(prev_img_downscaled_data[:,:curr_num_blocks+1,:]-curr_img_downscaled_data[:,:curr_num_blocks+1,:]).sum()
        if diff==0:
            return set()

    curr_err = np.square(curr_img_downscaled_data[:,:curr_num_blocks+1,:]-challenge_data[:,BLOCK:BLOCK+curr_num_blocks+1,:]).sum()
    curr_guesses = set([(curr_text, curr_err)])

    next_allowed_chars = get_next_allowed_chars(curr_text)
    for c in next_allowed_chars:
        # only explore new char if it changes current block
        next_text = curr_text + c
        recursive_guesses = get_block_charset(curr_num_blocks, next_text, curr_img_downscaled_data)
        curr_guesses.update(recursive_guesses)
    return curr_guesses


all_guesses = []

def run_trial(block, x_left_offset, y_top_offset, x_margin, y_margin, x_trim, y_trim):
    global BLOCK
    global X_MARGIN
    global Y_MARGIN
    global X_LEFT_OFFSET
    global Y_TOP_OFFSET
    global WIDTH_DELTA
    global HEIGHT_DELTA

    BLOCK = block
    X_MARGIN = x_margin
    Y_MARGIN = y_margin
    X_LEFT_OFFSET = x_left_offset
    Y_TOP_OFFSET = y_top_offset
    WIDTH_DELTA = x_trim
    HEIGHT_DELTA = y_trim
    # clear for each offset group

    curr_guesses = set([('', 1e99)])
    for curr_num_blocks in range(NUM_BLOCKS):
        print(f'testing block {block} { curr_num_blocks}')
        print(f'curr_guesses: {curr_guesses}')
        next_guesses = set([])
        for curr_text, curr_err in curr_guesses:
            print(f'testing {curr_text}')
            curr_next_guesses = get_block_charset(curr_num_blocks, curr_text)
            next_guesses.update(curr_next_guesses)
        next_guesses = sorted(list(next_guesses), key=lambda item:item[1])
        print(f'guesses for blocks {block}-{curr_num_blocks}')
        pprint.pprint(next_guesses[:10])
        if next_guesses[0][1] > MAX_ERROR:
            print('error too high')
            return []
        # keep best N guesses. Making this bigger can search more possibilities but takes longer.
        curr_guesses = set([g for g in next_guesses[:RETAINED_GUESSES] if g[1] <= MAX_ERROR])
    return next_guesses[:RETAINED_GUESSES]

def run_trials():
    all_guesses = []
    for block in [0]:
        for x_left_offset in X_LEFT_OFFSETS:
            for y_top_offset in Y_TOP_OFFSETS:
                for x_margin in X_MARGINS:
                    for y_margin in Y_MARGINS:
                        for x_trim in WIDTH_DELTAS:
                            for y_trim in HEIGHT_DELTAS:
                                print(f'checking offset block={block}, x_offset={x_left_offset}, y_offset={y_top_offset}, x_margin={x_margin}, y_margin={y_margin}, x_trim={x_trim}, y_trim={y_trim}')
                                curr_guesses = run_trial(block, x_left_offset, y_top_offset, x_margin, y_margin, x_trim, y_trim)
                                curr_guesses = [(test, err, block, x_left_offset, y_top_offset, x_margin, y_margin, x_trim, y_trim) for (test, err) in curr_guesses]
                                all_guesses.extend(curr_guesses)

    all_guesses = sorted(all_guesses, key=lambda item:item[1])
    return all_guesses

os.makedirs('results', exist_ok=True)

all_guesses = None
if METHOD=='Factorio':
    try:
        all_guesses = run_trials()
        all_guesses_df = pd.DataFrame(all_guesses, columns=['guess', 'score', 'block', 'left_offset', 'top_offset', 'x_margin', 'y_margin', 'x_trim', 'y_trim'])
        all_guesses_df.to_csv(os.path.join('results', f'guesses{IMAGE_NUM}.csv'))
    except:
        display_message('Error!')
        raise
else:
    all_guesses = run_trials()
    all_guesses_df = pd.DataFrame(all_guesses, columns=['guess', 'score', 'block', 'left_offset', 'top_offset', 'x_margin', 'y_margin', 'x_trim', 'y_trim'])
    all_guesses_df.to_csv(os.path.join('results', f'guesses{IMAGE_NUM}.csv'))


if METHOD=='Factorio':
    display_message('Done!')
