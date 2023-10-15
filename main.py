import itertools
import numpy as np
import os
import pprint
import string
from PIL import Image, ImageFont, ImageDraw
root_dir = os.path.realpath(os.path.join(__file__, '..'))

IMAGE_NUM = 5

# constants
PIXELS_PER_BLOCK = 4

FACTORIO_BACKGROUND_COLOR = (36, 35, 36)
BLACK = (0, 0, 0)

# see draw_nauvis
FONT = ImageFont.truetype("fonts/TitilliumWeb-Light.ttf", 14)

# can get stuck with the same error while generating new letters
MAX_LETTERS = 10

# always use these for every secret
HEIGHT_PIXELS = 20
HEIGHT_BLOCKS = 5
Y_TOP_OFFSET = 15

# from looking at the picture real close
X_LEFT_OFFSET = 0

# make generic later
IMAGE_FILENAME = os.path.join(root_dir, 'images', 'secrets', f'secret{IMAGE_NUM}.png')

def convert_to_block_array(image):
    data = np.asarray(image)

    # sum the rgbs, throw out the alphas
    grey = data[:,:,:3].sum(axis=2)

    # image y-direction is first array axis, x-direction is second array axis
    vert_blocks = image.height//PIXELS_PER_BLOCK
    horz_blocks = image.width//PIXELS_PER_BLOCK

    # not sure if this can be vectorized
    result = np.zeros((vert_blocks, horz_blocks))
    for i in range(vert_blocks):
        for j in range(horz_blocks):
            y_start = i*PIXELS_PER_BLOCK
            y_end = y_start+PIXELS_PER_BLOCK
            x_start = j*PIXELS_PER_BLOCK
            x_end = x_start+PIXELS_PER_BLOCK
            result[i,j] = grey[y_start:y_end, x_start:x_end].sum()

    return result

with Image.open(IMAGE_FILENAME).convert('RGBA') as image:
    challenge_width = image.width
    challenge_block = convert_to_block_array(image)

def generate_image_from_text(width, text, background=FACTORIO_BACKGROUND_COLOR):
    img  = Image.new( mode = "RGB", size = (width, HEIGHT_PIXELS), color=background)
    d = ImageDraw.Draw(img)
    d.text((X_LEFT_OFFSET, Y_TOP_OFFSET), font=FONT, text=text, anchor='ls')
    return img

def get_error(guess):
    curr_img = generate_image_from_text(challenge_width, guess)
    curr_block_array = convert_to_block_array(curr_img)
    err = np.square(challenge_block-curr_block_array).sum()
    return err

def block_has_data(block_num, text):
    img = generate_image_from_text(challenge_width, text, background=BLACK)
    block_array = convert_to_block_array(img)
    block_data = block_array[:, block_num].sum()
    return block_data>0

def block_err(block_num, text):
    img = generate_image_from_text(challenge_width, text, background=FACTORIO_BACKGROUND_COLOR)
    block_array = convert_to_block_array(img)
    return np.square(challenge_block[:,:block_num]-block_array[:,:block_num]).sum()

# block num is how many blocks to the right we are
def get_block_charset(block_num, prev_text):
    # include prev_text w/ curr block as a base case
    prev_err = block_err(block_num, prev_text)
    curr_guesses = set([(prev_text, prev_err)])

    # if the next block already has data we return early
    if block_has_data(block_num+1, prev_text):
        prev_err = block_err(block_num, prev_text)
        return curr_guesses

    next_allowed_chars = string.ascii_uppercase if prev_text=='' else string.ascii_lowercase
    for c in next_allowed_chars:
        curr_text = prev_text + c
        # if next block has no data then new chars could potentially affect current block, so recursively add more chars
        if not block_has_data(block_num+1, curr_text):
            recursive_guesses = get_block_charset(block_num, curr_text)
            curr_guesses.update(recursive_guesses)
        else:
            curr_err = block_err(block_num, curr_text)
            # only add new guess if it changes the error
            if prev_err != curr_err:
                curr_guesses.add( (curr_text, curr_err) )
    return curr_guesses

num_horiz_blocks = challenge_width//PIXELS_PER_BLOCK
curr_guesses = set([('', 1e99)])
for block in range(num_horiz_blocks-1):
    next_guesses = set([])
    for curr_text, curr_err in curr_guesses:
        next_guesses.update(get_block_charset(block, curr_text))
    next_guesses = sorted(list(next_guesses), key=lambda item:item[1])
    # keep best N guesses. Making this bigger can search more possibilities but takes longer.
    curr_guesses = set(next_guesses[:100])
    print(f'best guesses for block {block}')
    pprint.pprint(next_guesses[:10])

# incorporate last block into final error
curr_guesses = [(g, block_err(num_horiz_blocks, g)) for (g,err) in curr_guesses]
curr_guesses = sorted(next_guesses, key=lambda item:item[1])
print(f'final guess: {curr_guesses[0]}')

with Image.open(IMAGE_FILENAME).convert('RGBA') as image:
    d = ImageDraw.Draw(image)
    d.text((X_LEFT_OFFSET, Y_TOP_OFFSET), font=FONT, text=curr_guesses[0][0], anchor='ls')
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
