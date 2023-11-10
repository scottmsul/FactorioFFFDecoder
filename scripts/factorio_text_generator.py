import hashlib
import numpy as np
import os
import pyautogui
import pydirectinput
import time
from PIL import Image, ImageDraw, ImageFont
from util import add_margin

# instructions:
# set display resolution to 1920x1080
# install factory planner
# open factory planner
# create two FP floors
# start this script
# open Factorio window
# let it run! Uses pyautogui/pydirectinput to save images of text that *exactly match* the FFF's inputs.
# if you get stuck move the mouse to the upper-left of the screen to stop the script

FACTORIO_BACKGROUND_COLOR = (36, 35, 36)
PIXELS_PER_BLOCK = 4
TEXT_BOX_1_COORDS = (480, 165)
TEXT_BOX_2_COORDS = (480, 200)
TEXT_BOX_2_REGION = (237, 197, 60, 16)
TEXT_BOX_2_Y_OFFSET = 11 # number of pixels from top of text_box_2 that bottom of matches text line bottom

cache_dir = os.path.join('images', 'cache')

# gives time to switch to Factorio window before starting
# (could probably also use a window-switching method based on title name "Factorio")
def start_countdown():
    for i in range(5, 0, -1):
        print(f'starting in {i}..')
        time.sleep(1)

def get_filepath(text):
    os.makedirs(cache_dir, exist_ok=True)
    hashed = hashlib.sha256(str.encode(text)).hexdigest()
    filename = f'{hashed}.png'
    return os.path.abspath(os.path.join(cache_dir, filename))

def get_image(x_offset=0, y_offset=11, width=60, height=16, text='', use_cache=True):
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

def clear_image_from_cache(text):
    filepath = get_filepath(text)
    if os.path.exists(filepath):
        os.remove(filepath)

def get_raw_image(text, use_cache):
    if use_cache:
        filepath = get_filepath(text)
        try:
            img = Image.open(filepath)
            return img
        except Exception:
            pass
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
    pyautogui.screenshot()
    img = pyautogui.screenshot(region=TEXT_BOX_2_REGION)
    if use_cache:
        filepath = get_filepath(text)
        img.save(filepath)
    return img

def display_message(text):
    filepath = get_filepath(text)
    if os.path.isfile(filepath):
        img = Image.open(filepath)
        return img
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

### HELPER FUNCTIONS FOR TESTING ###
FONT = ImageFont.truetype("fonts/TitilliumTTF/TitilliumWeb-Regular.ttf", 14)

def generate_pillow_image(x_left_offset, y_top_offset, width, height, text):
    img  = Image.new( mode = "RGB", size = (width, height), color=FACTORIO_BACKGROUND_COLOR)
    d = ImageDraw.Draw(img)
    d.text((x_left_offset, y_top_offset), font=FONT, text=text, anchor='ls')
    return img

if __name__=='__main__':
    start_countdown()

    text = 'Custard'
    get_image(-1, 11, 60, 12, text)
    #clear_image_from_cache(text)

    #cra_img = get_image(-4, 12, 60, 12, 'cra')
    #craa_img = get_image(-4, 12, 60, 12, 'craa')
    #cra_img.save('cra_debug2.png')
    #craa_img.save('craa_debug2.png')
