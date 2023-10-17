import itertools
import numpy as np
import os
import pandas as pd
import pprint
import string
from english_words import get_english_words_set
from PIL import Image, ImageFont, ImageDraw
root_dir = os.path.realpath(os.path.join(__file__, '..'))

IMAGE_NUM = 5

RETAINED_GUESSES = 10

# constants
PIXELS_PER_BLOCK = 4

FACTORIO_BACKGROUND_COLOR = (36, 35, 36)
BLACK = (0, 0, 0)

# see draw_nauvis
FONT = ImageFont.truetype("fonts/TitilliumWeb-Regular.ttf", 14)

# can get stuck with the same error while generating new letters
MAX_LETTERS = 10

# always use these for every secret
HEIGHT_PIXELS = 20
HEIGHT_BLOCKS = 5
Y_ORIG_TOP_OFFSET = 15

# from looking at the picture real close
X_ORIG_LEFT_OFFSET = 0

X_LEFT_OFFSET = -1
Y_TOP_OFFSET = 15

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

words = get_english_words_set(['web2'], lower=True)
words = [w.title() for w in words]
num_words = len(words)
best_err = 1e99
best_word = None
results = []
for i, word in enumerate(words):
    if i%1000==0:
        print(f'word {i}/{num_words}')
    err = get_error(word)
    results.append((word, err))

results = sorted(results, key=lambda item: item[1])
results = results[:1000]
df = pd.DataFrame(results, columns=['word', 'error'])

print(f'best word: {best_word}')
print(f'best err: {best_err}')

df.to_csv(os.path.join('guesses', f'guesses{IMAGE_NUM}_words.csv'))
#
# with Image.open(IMAGE_FILENAME).convert('RGBA') as image:
#     d = ImageDraw.Draw(image)
#     d.text((X_LEFT_OFFSET, Y_TOP_OFFSET), font=FONT, text=all_guesses[0][0], anchor='ls')
#     image.save(os.path.join('images', 'results', f'result{IMAGE_NUM}.png'))

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
