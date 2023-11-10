import argparse
import hashlib
import numpy as np
import os
import pyautogui
import pydirectinput
import time
from argparse import RawTextHelpFormatter
from PIL import Image, ImageDraw, ImageFont
from util import add_margin

FACTORIO_BACKGROUND_COLOR = (36, 35, 36)
TEXT_BOX_1_COORDS = (480, 165)
TEXT_BOX_2_COORDS = (480, 200)
TEXT_BOX_2_REGION = (237, 197, 60, 16)
TEXT_BOX_2_Y_OFFSET = 11 # number of pixels from top of text_box_2 that bottom of matches text line bottom

cache_dir = os.path.join('images', 'cache')

def start_countdown():
    '''
    Five-second countdown.
    Gives user time to switch to Factorio window.
    '''
    for i in range(5, 0, -1):
        print(f'starting in {i}..')
        time.sleep(1)

def get_filepath(text):
    '''
    Returns cache filename for a given text.
    '''
    os.makedirs(cache_dir, exist_ok=True)
    hashed = hashlib.sha256(str.encode(text)).hexdigest()
    filename = f'{hashed}.png'
    return os.path.abspath(os.path.join(cache_dir, filename))

def get_image(x_offset=0, y_offset=11, width=60, height=16, text='', use_cache=True):
    '''
    Returns an appropriately offset, cropped, and padded image for a given text.

    x_offset: Horizontal pixel offset between text bottom-left corner and left edge of image
    y_offset: Vertical pixel offset between text bottom-left corner and top edge of image
    width: Width of returned image in pixels.
    height: Height of returned image in pixels.
    text: text to generate
    use_cache: Whether to use the cache. If False, then re-generate the text and don't save to cache.
    '''
    raw_img = get_raw_image(text, use_cache)

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

def check_if_cached(text):
    '''
    Checks whether a given text is already cached
    '''
    filepath = get_filepath(text)
    return os.path.exists(filepath)

def clear_image_from_cache(text):
    '''
    Deletes a given text from the cache if it exists
    '''
    filepath = get_filepath(text)
    if os.path.exists(filepath):
        os.remove(filepath)

def get_raw_image(text, use_cache):
    '''
    Snapshots an image of a string of text generated in Factorio.
    '''
    if use_cache:
        filepath = get_filepath(text)
        try:
            img = Image.open(filepath)
            return img
        except Exception:
            pass
    display_message(text)
    img = pyautogui.screenshot(region=TEXT_BOX_2_REGION)
    if use_cache:
        filepath = get_filepath(text)
        img.save(filepath)
    return img

def display_message(text):
    '''
    Displays a given text as the second subfactory in Factory Planner.
    Useful for both get_raw_image and displaying custom messages, such as when a script is finished or errors out.
    '''
    pyautogui.moveTo(*TEXT_BOX_2_COORDS)
    pyautogui.click(button='right')
    pydirectinput.keyDown('ctrl')
    pydirectinput.press('a')
    pydirectinput.keyUp('ctrl')
    pydirectinput.press('backspace')
    pyautogui.write(text)
    pydirectinput.press('enter')
    pyautogui.moveTo(*TEXT_BOX_1_COORDS)
    pyautogui.click()
    # if it screenshots too fast, sometimes leaves orange background
    time.sleep(0.1)

### helper function for testing, used to make sure offsets and width/height match equivalent pillow functions ###
FONT = ImageFont.truetype("fonts/TitilliumTTF/TitilliumWeb-Regular.ttf", 14)

def generate_pillow_image(x_left_offset, y_top_offset, width, height, text):
    img  = Image.new( mode = "RGB", size = (width, height), color=FACTORIO_BACKGROUND_COLOR)
    d = ImageDraw.Draw(img)
    d.text((x_left_offset, y_top_offset), font=FONT, text=text, anchor='ls')
    return img

HELP_DESCRIPTION = '''
This python module allows for generating and screen capturing text from a running Factorio instance.
Note that this has only been tested in Windows.

Instructions:
1) Set display resolution to 1920x1080
2) Open Factorio
3) Install Factory Planner mod
4) Start a new game
5) Open Factory Planner (Ctrl+r)
6) Create two subfactories using the green "+" in the upper-left. Name them each "a".
7) Launch or call this script. During the five-second countdown switch to the Factorio window.
8) Watch as the mouse randomly moves around and magically types and screenshots text!

Use as a standalone script isn't that interesting on its own and is more to test that the code is working properly.

This module can be used in an automated and controlled way using the 'get_image' function.
It's strongly advised to call the 'start_countdown' and 'display_message' at the start and end of other scripts relying on this code.
Images are cached in 'images/cache' to significantly speedup scripts by not having to generate the same text twice.
All images use Python's Pillow format internally.
'''

if __name__=='__main__':
    parser = argparse.ArgumentParser(prog='Factorio Text Generator', description=HELP_DESCRIPTION, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-t', '--text', help='text to screenshot', required=True)
    args = parser.parse_args()
    start_countdown()

    text = args.text
    image = get_raw_image(text, use_cache=False)
    image.show()
