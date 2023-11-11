'''
This is a standalone script that takes a set of texts and image configurations as input,
and computes a sorted list of the best (lowest error) configurations as output.
This script doesn't do any argparsing, to customize it change the variables at the top.
A simple example is shown - suppose we suspect the word for secret 1 might be "Vulcanus",
but we don't know how it's positioned or cropped or padded.
    top 5 results:
    text	    x_offset	y_offset	top	bottom	left	right	left_err
    Vulcanus	-1	11	0	0	0	0	53
    Vulcanus	-1	11	1	0	0	0	5032
    Vulcanus	-1	11	0	0	0	1	8616
    Vulcanus	-1	11	0	0	0	-1	10656
    Vulcanus	-2	11	0	0	0	-2	10949
We can see the correct x_offset, y_offset is 100x better than one pixel off.
When the method is 'magick_linux' on wsl the error is zero, but this is tricky to run, as importing pyautogui crashes it.

This script can iterate over all possible x/y offsets for the text, different widths/heights, downscaling algorithms, etc.,
until it finds the configuration with the best match. Results are saved in 'results/check_word_results.csv'.
One way to use this script is to try to matching invididual letters or groups of letters by setting the start and end blocks.
'''
import itertools
import os
import pandas as pd
import pprint
from check_word import check_word, check_word_pixels
from factorio_text_generator import start_countdown, check_if_cached, display_message

if __name__=='__main__':
    image_num = 1
    downscale_mode = 'magick_windows'
    start_block = 0
    end_block = 0

    # for now don't change bottom or left because that's redundant with the x and y offsets
    texts = ['Vulcanus']
    x_offsets = [-2, -1, 0, 1]
    y_offsets = [10, 11, 12, 13]
    tops = [-2, -1, 0, 1]
    bottoms = [0]
    lefts = [0]
    rights = [-2, -1, 0, 1]

    all_cached = all([check_if_cached(text) for text in texts])
    if not all_cached:
        start_countdown()

    secret = os.path.join('images', 'secrets', f'secret{image_num}.png')
    prev_text = ''
    best_config = None
    min_err = 1e99
    values = []
    for text, x_offset, y_offset, top, bottom, left, right in itertools.product(texts, x_offsets, y_offsets, tops, bottoms, lefts, rights):
        if text != prev_text:
            print(f'checking {text}')
            prev_text = text
        err = check_word(text, secret, downscale_mode, start_block, end_block, x_offset, y_offset, top, bottom, left, right)
        if err < min_err:
            best_config = (text, x_offset, y_offset, top, bottom, left, right)
            min_err = err
        values.append([text, x_offset, y_offset, top, bottom, left, right, err])
        print(f'text: {text}, x_offset: {x_offset}, y_offset: {y_offset}, top: {top}, bottom: {bottom}, left: {left}, right: {right}')
        print(err)

    if not all_cached:
        display_message('done!')

    df = pd.DataFrame(values, columns=['text', 'x_offset', 'y_offset', 'top', 'bottom', 'left', 'right', 'left_err'])
    df = df.sort_values(by=['left_err'])
    os.makedirs('results', exist_ok=True)
    output_filepath = os.path.join('results', 'check_word_results.csv')
    df.to_csv(output_filepath, index=False)

    print('best 10 results')
    for i,row in itertools.islice(df.iterrows(), 10):
        print('')
        pprint.pprint(row)
        err_pixels = check_word_pixels(row['text'], secret, downscale_mode, start_block, end_block, row['x_offset'], row['y_offset'], row['top'], row['bottom'], row['left'], row['right'])
        print(err_pixels)
