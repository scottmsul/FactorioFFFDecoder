import itertools
import numpy as np
import os
import pandas as pd
import pprint
import string
from PIL import Image, ImageFont, ImageDraw
root_dir = os.path.realpath(os.path.join(__file__, '..'))

np.random.seed(123456)

IMAGE_NUM = 5
RETAINED_GUESSES = 1000

# images 1, 2, 3, 4 all prefer (-1, 11)
# image 5 prefers x in [-2, -1, 0] and y=12
X_LEFT_OFFSETS = [-2, -1, 0]
Y_TOP_OFFSETS = [11]
# X_LEFT_OFFSETS = [-1]
# Y_TOP_OFFSETS = [11]
#X_LEFT_OFFSETS = [-2, -1, 0, 1, 2]
#Y_TOP_OFFSETS = [9, 10, 11, 12, 13]

#RESAMPLING_METHOD = Image.Resampling.NEAREST
#RESAMPLING_METHOD = Image.Resampling.BILINEAR
RESAMPLING_METHOD = Image.Resampling.BOX
#RESAMPLING_METHOD = Image.Resampling.HAMMING
#RESAMPLING_METHOD = Image.Resampling.BICUBIC
#RESAMPLING_METHOD = Image.Resampling.LANCZOS

PENALIZE_LAST_BLOCK = True

# constants
PIXELS_PER_BLOCK = 4

FACTORIO_BACKGROUND_COLOR = (36, 35, 36)
#FACTORIO_BACKGROUND_COLOR = (0, 0, 0)
BLACK = (0, 0, 0)

X_LEFT_OFFSET = None
Y_TOP_OFFSET = None

# see draw_nauvis
#FONT = ImageFont.truetype("fonts/TitilliumTTF/TitilliumWeb-Light.ttf", 14)
FONT = ImageFont.truetype("fonts/TitilliumTTF/TitilliumWeb-Regular.ttf", 14)
#FONT = ImageFont.truetype("fonts/TitilliumOTF/Titillium-Regular.otf", 14)

# can get stuck with the same error while generating new letters
MAX_LETTERS = 10

# always use these for every secret
# HEIGHT_PIXELS = 20
# HEIGHT_BLOCKS = 5

# make generic later
IMAGE_FILENAME = os.path.join(root_dir, 'images', 'secrets', f'secret{IMAGE_NUM}.png')
challenge_image = Image.open(IMAGE_FILENAME).convert('RGB')
challenge_data = np.asarray(challenge_image)[::PIXELS_PER_BLOCK, ::PIXELS_PER_BLOCK, :3]
challenge_width = challenge_image.width
WIDTH_BLOCKS = challenge_width // PIXELS_PER_BLOCK

HEIGHT_PIXELS = challenge_image.height
HEIGHT_BLOCKS = HEIGHT_PIXELS//PIXELS_PER_BLOCK

# dynamic programming
IMAGES = {}

# def convert_to_block_array(image):
#     data = np.asarray(image)
#
#     # sum the rgbs, throw out the alphas
#     grey = data[:,:,:3].sum(axis=2)
#
#     # image y-direction is first array axis, x-direction is second array axis
#     vert_blocks = image.height//PIXELS_PER_BLOCK
#     horz_blocks = image.width//PIXELS_PER_BLOCK
#
#     # not sure if this can be vectorized
#     result = np.zeros((vert_blocks, horz_blocks))
#     for i in range(vert_blocks):
#         for j in range(horz_blocks):
#             y_start = i*PIXELS_PER_BLOCK
#             y_end = y_start+PIXELS_PER_BLOCK
#             x_start = j*PIXELS_PER_BLOCK
#             x_end = x_start+PIXELS_PER_BLOCK
#             result[i,j] = grey[y_start:y_end, x_start:x_end].sum()
#
#     return result

def downscale(image):
    new_width = image.width // PIXELS_PER_BLOCK
    new_height = image.height // PIXELS_PER_BLOCK
    downscaled = image.resize((new_width,new_height), resample=RESAMPLING_METHOD)
    return downscaled

def pixelate(image):
    return downscale(image).resize(image.size, Image.Resampling.NEAREST)

# with Image.open(IMAGE_FILENAME).convert('RGBA') as image:
#     vert_blocks = image.height//PIXELS_PER_BLOCK
#     horz_blocks = image.width//PIXELS_PER_BLOCK
#     challenge_width = image.width
#     challenge_block = convert_to_block_array(image)

def generate_image_from_text(width, text, background=FACTORIO_BACKGROUND_COLOR):
    img  = Image.new( mode = "RGB", size = (width, HEIGHT_PIXELS), color=background)
    d = ImageDraw.Draw(img)
    d.text((X_LEFT_OFFSET, Y_TOP_OFFSET), font=FONT, text=text, anchor='ls')
    return img

def get_error(guess):
    curr_img = generate_image_from_text(challenge_width, guess)
    curr_downscaled = downscale(curr_img)
    curr_downscaled_data = np.asarray(curr_downscaled)[:,:,:3]
    err = np.square(challenge_data-curr_downscaled_data).sum()
    #err = np.abs(challenge_image-curr_pixelated).sum()
    return err

def block_has_data(block_num, text):
    img = generate_image_from_text(challenge_width+PIXELS_PER_BLOCK, text, background=BLACK)
    downscaled_data = np.asarray(downscale(img))[:,:,:3]
    block_data = downscaled_data[:, block_num, :].sum()
    return block_data>0

def block_err(block_num, text):
    img = generate_image_from_text(challenge_width, text, background=FACTORIO_BACKGROUND_COLOR)
    downscaled_data = np.asarray(downscale(img))[:,:,:3]
    return np.square(challenge_data[:,:block_num,:]-downscaled_data[:,:block_num,:]).sum()
    #return np.abs(challenge_data[:,:block_num,:]-downscaled_data[:,:block_num,:]).sum()

# block num is how many blocks to the right we are
def get_block_charset(block_num, curr_text, prev_img_downscaled_data=None):
    #print(curr_text)
    if curr_text in IMAGES:
        curr_img_downscaled_data = IMAGES[curr_text]
    else:
        curr_img = generate_image_from_text(challenge_image.width+PIXELS_PER_BLOCK, curr_text, background=FACTORIO_BACKGROUND_COLOR)
        curr_img_downscaled = downscale(curr_img)
        curr_img_downscaled_data = np.asarray(curr_img_downscaled)[:, :, :3]
        IMAGES[curr_text] = curr_img_downscaled_data

    # if adding the new letter doesn't change the block data, don't include in the charset
    if (prev_img_downscaled_data is not None):
        diff = np.square(prev_img_downscaled_data[:,:block_num+1,:]-curr_img_downscaled_data[:,:block_num+1,:]).sum()
        if diff==0:
            return set()

    # try adding white noise to reduce over-fitting (????)
    # r = np.random.normal(1, .01, curr_img_downscaled_data.shape)
    # mask = curr_img_downscaled_data!=FACTORIO_BACKGROUND_COLOR
    # curr_img_downscaled_data[mask] *= r[mask]

    curr_err = np.square(curr_img_downscaled_data[:,:block_num+1,:]-challenge_data[:,:block_num+1,:]).sum()
    curr_guesses = set([(curr_text, curr_err)])

    # if block_num==(WIDTH_BLOCKS-1):
    #     print('last block')
    #     print(f'text: {curr_text}')
    #     print(f'curr_err: {curr_err}')
    #     print(f'calling get_error: {get_error(curr_text)}')
    #     raise

    # next_block_has_data = (curr_img_downscaled_data[:,block_num+1,:]>FACTORIO_BACKGROUND_COLOR).sum()
    # if next_block_has_data:
    #     return curr_guesses

    next_allowed_chars = string.ascii_uppercase if curr_text=='' else string.ascii_lowercase
    #next_allowed_chars = string.ascii_uppercase + string.ascii_lowercase
    if HEIGHT_BLOCKS==3:
        next_allowed_chars = next_allowed_chars.replace('g', '').replace('j', '').replace('p', '').replace('q', '').replace('y', '')
    for c in next_allowed_chars:
        # only explore new char if it changes current block
        next_text = curr_text + c
        recursive_guesses = get_block_charset(block_num, next_text, curr_img_downscaled_data)
        curr_guesses.update(recursive_guesses)
        # next_img = generate_image_from_text(challenge_image.width+PIXELS_PER_BLOCK, next_text, background=FACTORIO_BACKGROUND_COLOR)
        # curr_img_data = np.asarray(curr_img)[:, :, :3]
        # next_img_data = np.asarray(next_img)[:, :, :3]
        # diff = np.square(curr_img_data[:,:(PIXELS_PER_BLOCK*(block_num+1)),:]-next_img_data[:,:(PIXELS_PER_BLOCK*(block_num+1)),:]).sum()
        # if diff>0:
        #     recursive_guesses = get_block_charset(block_num, next_text)
        #     curr_guesses.update(recursive_guesses)
        # else:
        #     break
    return curr_guesses


# # TEST
# X_LEFT_OFFSET = -1
# Y_TOP_OFFSET = 11
# err = get_error('Ilirzeuzlh')
# print(f'Ilirzeuzlh: {err}')
# raise

all_guesses = []
#for additional_x_offset in np.linspace(-3, 3, 7):
for X_LEFT_OFFSET in X_LEFT_OFFSETS:
    for Y_TOP_OFFSET in Y_TOP_OFFSETS:
        # clear for each offset group
        IMAGES = {}

        print(f'checking offset x={X_LEFT_OFFSET}, y={Y_TOP_OFFSET}')
        curr_guesses = set([('', 1e99)])
        for block in range(WIDTH_BLOCKS):
            print(f'testing block {block}')
            next_guesses = set([])
            for curr_text, curr_err in curr_guesses:
                next_guesses.update(get_block_charset(block, curr_text))
            next_guesses = sorted(list(next_guesses), key=lambda item:item[1])
            print(f'guesses for block {block}')
            pprint.pprint(next_guesses[:10])
            # keep best N guesses. Making this bigger can search more possibilities but takes longer.
            curr_guesses = set(next_guesses[:RETAINED_GUESSES])
        curr_guesses = [(test, err, X_LEFT_OFFSET, Y_TOP_OFFSET) for (test, err) in curr_guesses]
        all_guesses.extend(curr_guesses)
all_guesses = sorted(all_guesses, key=lambda item:item[1])


# # incorporate last block into final error
# all_guesses = [(g, block_err(WIDTH_BLOCKS, g), x, y) for (g,_,x,y) in all_guesses]
# all_guesses = sorted(all_guesses, key=lambda item:item[1])
# print(f'final guess: {all_guesses[0]}')
#
all_guesses_df = pd.DataFrame(all_guesses, columns=['guess', 'score', 'left_offset', 'top_offset'])
all_guesses_df.to_csv(os.path.join('guesses', f'guesses{IMAGE_NUM}.csv'))
#
with Image.open(IMAGE_FILENAME).convert('RGBA') as image:
    d = ImageDraw.Draw(image)
    d.text((X_LEFT_OFFSET, Y_TOP_OFFSET), font=FONT, text=all_guesses[0][0], anchor='ls')
    image.save(os.path.join('images', 'results', f'result{IMAGE_NUM}.png'))

# I tried a previous approach that was letter-based rather than block-based but the results weren't as good
# prev_best_err = 1e99
# starting_texts = list(string.ascii_uppercase)
# all_guesses = set()
# curr_guesses = [(g, get_error(g)) for g in starting_texts]
# curr_guesses = [('', 0)]
# i = 0
# while True:
#     i += 1
#     print(f'letter # : {i}')
#     print(f'curr_guesses: {curr_guesses}')
#     print(f'best err: {prev_best_err}')
#
#     # start simple/naive, do the two-guess stuff later
#     # new_text_appends = list(string.ascii_lowercase)
#
#     # guess letters two-at-a-time
#     new_next_letters = string.ascii_uppercase if i==1 else string.ascii_lowercase+' '
#     new_text_appends = [''.join(i) for i in itertools.product(string.ascii_lowercase+' ', repeat = 2)]
#
#     # debug info to track progress
#     j = 0
#     num_new_guesses = len(curr_guesses)*len(new_next_letters)
#
#     next_guesses = []
#     for curr_text, curr_err in curr_guesses:
#         for new_next_letter in new_next_letters:
#             j += 1
#             print(f'guesses so far: {j}/{num_new_guesses}')
#             lowest_curr_err = 1e99
#             for new_text_append in new_text_appends:
#                 new_text = curr_text + new_next_letter + new_text_append
#                 new_err = get_error(new_text)
#                 lowest_curr_err = min(lowest_curr_err, new_err)
#             next_letter_info = (curr_text+new_next_letter, lowest_curr_err)
#             next_guesses.append(next_letter_info)
#             all_guesses.add(next_letter_info)
#     next_guesses = sorted(next_guesses, key=lambda item: item[1])
#     curr_best_err = next_guesses[0][1]
#     if prev_best_err < curr_best_err or i > MAX_LETTERS:
#         break
#     prev_best_err = curr_best_err
#     # only take best N each time as ad-hoc optimization
#     curr_guesses = next_guesses[:20]
