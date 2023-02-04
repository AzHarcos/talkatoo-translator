"""
This Python script takes the broad approach:
    Retrieve video footage from USB capture card
    Check for possibility of text in a few ways
    Preprocess game feed for better Optical Character Recognition
    Use OCR to look for Talkatoo text in any supported language
    Output the translated version and other close matches
"""

import cv2  # pip install opencv-python
import eel  # pip install eel
import json
import numpy as np  # pip install numpy
import os
from PIL import Image  # pip install pillow
import platform
import psutil  # pip install psutil
import pytesseract  # pip install pytesseract
                    # Then install language files from https://github.com/tesseract-ocr/tessdata and place in tessdata
import time
import torch  # pip install pytorch
import torchvision.transforms as transforms  # should come with pytorch


# parameters that could be set in the gui: capture card resolution, game language, output language, kingdom list (which kingdoms + which order)

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"  # Path to tesseract executable
TRANSLATE_FROM_TESS = "chi_tra"  # Use Tesseract codes, chi_sim for Simplified Chinese or chi_tra for Traditional Chinese
LANGUAGES = ["english", "chinese_traditional", "chinese_simplified", "japanese", "korean", "dutch", "french_canada",
             "french_france", "german", "italian", "spanish_spain", "spanish_latin_america", "russian"]
TRANSLATE_FROM = "chinese_traditional"  # Language to translate from, moon-list.json keys
TRANSLATE_TO = "english"  # Language you want to translate to, moon-list.json keys

CHECK_KINGDOM_EVERY = 40  # Currently iterations are ~0.05s each
KINGDOM_CERTAINTY = 0.85  # Classifier certainty to prevent uncertain kingdom switches (must occur 2 times in a row)
POSS_MOON_CERTAINTY = 0.1  # Show moon percentage if it's at least 10% possible
SCORE_THRESHOLD = -2  # Score from score_func where a moon can be considered for correctness, -1.5 or 2 is about right
TEXT_CERTAINTY = 0.90  # Classifier certainty that the input is text and not random pixels

IM_WIDTH = 1280  # Don't change! Testing this way for time save on resizing
IM_HEIGHT = 720  # Don't change! Testing this way for time save on resizing
MIN_TEXT_COUNT = 400  # Number of pixels to count as text, don't change unless moon names aren't seen
VIDEO_INDEX = 0  # Usually capture card is 0, but if you have other video sources it may not be


# Checks recognized text against moons fromm the current kingdom
def check_matches(poss_moon, story=False):
    max_corr = -100  # so low it will never matter
    ans = []  # best matches
    poss_matches = {}  # Loose matches
    for i, m in enumerate(moons_by_kingdom[current_kingdom]):  # Loop through moons in the current kingdom
        corr = score_func(m[TRANSLATE_FROM], poss_moon)  # Determine score for moon being compared
        if corr >= SCORE_THRESHOLD:  # Loose match, we don't need this but could situationally be useful
            poss_matches[m[TRANSLATE_TO]] = corr
            if corr > max_corr:  # Best match so far
                max_corr = corr
                ans = [m]
            elif corr == max_corr:  # Equally good as best match
                ans.append(m)
        if i == 7 and story:
            break
    poss_matches = score_to_pct(poss_matches)
    return max_corr, ans, poss_matches


# Very ugly and naive checker for story/multi moon
def check_story_multi(img, expected="RED"):
    if expected == "RED":
        min_red, max_red = 6400, 6400
        min_white, max_white = 0, 0
        min_blue, max_blue = 0, 0
    elif expected == "STORY":
        min_red, max_red = 4350, 4500
        min_white, max_white = 500, 700
        min_blue, max_blue = 450, 600
    elif expected == "MULTI":
        min_red, max_red = 4050, 4200
        min_white, max_white = 200, 500
        min_blue, max_blue = 700, 900
    else:
        return False
    image_arr = np.array(img)
    red = image_arr[:, :, 0] > 200
    blue_green = np.logical_and(image_arr[:, :, 1] > 200, image_arr[:, :, 2] > 200)
    white_count_right = min_white <= np.logical_and(red, blue_green).sum() <= max_white
    red_count_right = min_red <= np.logical_and(red, np.logical_not(blue_green)).sum() <= max_red
    blue_count_right = min_blue <= np.logical_and(blue_green, np.logical_not(red)).sum() <= max_blue
    return red_count_right and white_count_right and blue_count_right


# Replace certain known problematic characters to make better matches
def correct(string):
    replacements = {}
    if TRANSLATE_FROM.startswith("chinese"):  # Designed from
        replacements = {" ": "", "，": "‧", ".": "‧", "!": "！", "『": "！", "|": "１", "]": "１", "１": "１", "鑾": "", "}": "！",
                        "”": "", "ˋ": "", "\"": "", "'": "", "‵": "", "(": "", ")": "", "1": "１", "2": "２", "3": "３"}
    for i in replacements:
        string = string.replace(i, replacements[i])
    return string


# Used to set capture card borders, for cropping to work the game must be the whole screen
def determine_borders(im):
    min_x, max_x, min_y, max_y = 0, im.width-1, 0, im.height-1
    thresh_x = 20  # some cc error, but if sum of RGB for an entire row or column is less than this,
    thresh_y = 20  # we can consider it to be black. 12 has worked for me but 20 to be slightly safer.
    for i in range(im.width):
        col_sum = max([sum(im.getpixel((i, j))) for j in range(im.height)])
        min_x += 1
        if col_sum > thresh_x:
            break
    for i in range(im.width-1, 0, -1):
        col_sum = max([sum(im.getpixel((i, j))) for j in range(im.height)])
        if col_sum > thresh_x:
            break
        max_x -= 1
    for j in range(im.height):
        col_sum = max([sum(im.getpixel((i, j))) for i in range(im.width)])
        min_y += 1
        if col_sum > thresh_y:
            break
    for j in range(im.height-1, 0, -1):
        col_sum = max([sum(im.getpixel((i, j))) for i in range(im.width)])
        if col_sum > thresh_y:
            break
        max_y -= 1
    # Defaults
    if max_x - min_x < im.width / 2:
        min_x = 0
        max_x = im.width - 1
    if max_y - min_y < im.height / 2:
        min_y = 0
        max_y = im.height - 1
    return min_x, min_y, max_x, max_y


# Expose the moons given by talkatoo to the gui
@eel.expose
def get_mentioned_moons():
    return mentioned_moons


# Expose the kingdom moons dictionary to the gui
@eel.expose
def get_moons_by_kingdom():
    return moons_by_kingdom


# checks if moon text is possibly present
def is_moon(img):
    img = img.resize((400, 40))
    new_im_arr = np.ones((50, 650, 3)).astype(np.uint8) * 255
    new_im_arr[5:-5, 125:-125] = np.array(img)
    new_im = Image.fromarray(new_im_arr)
    return is_text(new_im, cert=0.5)


# Checks to see if image is talkatoo text or random pixels
def is_text(img, cert=TEXT_CERTAINTY):
    tc_tensor = transform(img).unsqueeze(dim=0).type(torch.float32)
    probs = torch.softmax(text_classifier(tc_tensor), dim=1)
    return probs[0][0] >= cert  # 0 means it's text, 1 means it's not. So this returns False for no text/uncertain


# Make black and white image of purple coin counter
def image_to_bw(img, white=240):
    image_arr = np.array(img)
    red = image_arr[:, :, 0] <= white
    green = image_arr[:, :, 1] <= white
    blue = image_arr[:, :, 2] <= white
    image_arr[:, :, 0] = np.maximum.reduce([red, green, blue]) * 255  # if any untrue make white, else black
    image_arr[:, :, 1] = image_arr[:, :, 2] = image_arr[:, :, 0]
    return Image.fromarray(image_arr.astype(np.uint8))


# Recognize, clean, and check moon text
def match_moon_text(moon_img, prepend="Unlocked", story=False):
    print("Going to OCR... ", end="")
    ocr_text = pytesseract.image_to_string(moon_img, lang=TRANSLATE_FROM_TESS, config='--psm 6')
    ocr_text = correct(ocr_text.strip())
    print("Finished OCR -> ", end="")
    if len(ocr_text) < 3:
        return None

    max_corr, ans, possible = check_matches(ocr_text, story=story)
    if max_corr >= SCORE_THRESHOLD:  # If any reasonable matches, lower by one if story moon
        best_matches = len(ans)
        if best_matches == 1:
            print(prepend, "a moon: {} (score={})".format(ans[0]["english"], max_corr))
        else:
            print(prepend, "multiple moons({} total): {} (score={})".format(best_matches, " OR ".join([poss["english"] for poss in ans]), max_corr))
        print(possible, end="\n\n")
        return ans
    print(possible, end="\n\n")
    return None


# Replacement Levenshtein distance cost function
# May not be as effective with English alphabet as spurious character matches will be far more common, and thresholds are different
def score_func(proper_moon, test_moon):
    proper_len = len(proper_moon)
    test_len = len(test_moon)
    len_diff = proper_len - test_len
    if len_diff > 3:
        return -10
    fail_out = SCORE_THRESHOLD - 2 - (proper_len / 4)
    cost = max(len_diff/2, 0)  # Penalize missing characters 1.5x as much as the rest
    cor = 0.5 if proper_len == test_len else 0  # Give an extra half point if the length is exact

    # Ordered character search
    trav_index = 0
    for c in proper_moon:
        ind = trav_index
        found = False
        while ind < test_len:
            if test_moon[ind] == c:
                found = True
                trav_index = ind + 1
                break
            ind += 1
        if found:
            cor += 1
        else:
            cost += 1
        if cor - cost <= fail_out:  # if the score is bad enough then don't bother
            return -10
    return cor - cost


# Translate scores to percent certainty
def score_to_pct(poss_moon_dict):
    poss_moon_dict["Uncertain"] = SCORE_THRESHOLD
    keys = list(poss_moon_dict.keys())
    percents = torch.softmax(torch.tensor([float(poss_moon_dict[key]) for key in poss_moon_dict]), dim=0)
    return {keys[i]: round(float(percents[i])*100, 2) for i in range(len(keys)) if percents[i] > POSS_MOON_CERTAINTY}


# Preprocess talkatoo text box, yellow text becomes black while all else becomes white
def talkatoo_preprocess_better(talk_img, kingd):
    image_arr = np.array(talk_img)
    if kingd in ["Metro", "Seaside"]:
        r_min, g_min, b_max = 220, 220, 120  # Problem kingdoms
    else:
        r_min, g_min, b_max = 200, 200, 150  # Looser numbers usually work
    red = image_arr[:, :, 0] <= r_min
    green = image_arr[:, :, 1] <= g_min
    blue = image_arr[:, :, 2] >= b_max
    image_arr[:, :, 0] = np.maximum.reduce([red, green, blue]) * 255  # if any untrue make white, else black
    image_arr[:, :, 1] = image_arr[:, :, 2] = image_arr[:, :, 0]
    text_count = np.sum(image_arr[:, :, 0] == 0)
    return Image.fromarray(image_arr.astype(np.uint8)), text_count > MIN_TEXT_COUNT


# Check kingdom via recognition and update it if needed
def update_kingdom(img):
    kc_tensor = transform(img).unsqueeze(dim=0).type(torch.float32)
    probs = torch.softmax(kindom_classifier(kc_tensor), dim=1)
    result = int(torch.argmax(probs))
    if result != 13 and probs[0][result] > KINGDOM_CERTAINTY:  # 13 is "Other" in my model
        return kingdom_list[result], CHECK_KINGDOM_EVERY
    return None, 10  # Was not able to determine kingdom, check in 10 iterations hoping that something's changed


# Read moon translation data
with open("moon-list.json", encoding="utf8") as moon_file:
    moonlist = "".join([line.strip() for line in moon_file.readlines()])
    moonlist = json.loads(moonlist)  # moonlist now a list of dictionaries, one for each moon

# Dictionary to store all moons by kingdom
# Language indexing as follows: kingdoms["Cap"]["chinese_moon"]["language_name"]
moons_by_kingdom = {}
for moon in moonlist:
    this_kingdom = moon["kingdom"]
    this_moon = {"id": moon["id"], "kingdom": moon["kingdom"], TRANSLATE_FROM: moon[TRANSLATE_FROM],
                 TRANSLATE_TO: moon[TRANSLATE_TO], "chinese_simplified": moon["chinese_simplified"]}
    if this_kingdom in moons_by_kingdom:
        moons_by_kingdom[this_kingdom].append(this_moon)
    else:
        moons_by_kingdom[this_kingdom] = [this_moon]

kingdom_list = ("Cap", "Cascade", "Sand", "Lake", "Wooded", "Lost", "Metro", "Seaside",
                "Snow", "Luncheon", "Bowsers", "Moon", "Mushroom")  # to store class values, DO NOT CHANGE ORDER
current_kingdom = kingdom_list[-3]  # Start in first kingdom (fine to start in Cap)
mentioned_moons = []  # list of moons mentioned by Talkatoo
collected_moons = []  # list of auto-recognized collected moons

# Load kingdom and text recognizers
kindom_classifier = torch.jit.load("KingdomModel.zip")  # Pretrained kingdom recognizer, output 0-13 inclusive
text_classifier = torch.jit.load("TextModel.zip")  # Pretrained text classifier, output 0 or 1
transform = transforms.PILToTensor()  # Needed to transform image

# This is to ensure a more reliable runtime, if you tab out then the program runs slower due to caching,
# which can cause performance issues (missed moons)
this_OS = platform.system()
if this_OS == "Windows":
    p = psutil.Process(os.getpid())
    p.nice(psutil.REALTIME_PRIORITY_CLASS)  # For Windows, highest priority
elif this_OS == "Linux" or this_OS == "Darwin":  # Darwin signifies Mac
    p = psutil.Process(os.getpid())
    p.nice(15)  # 20 is max

# Final setup variables
change_kingdom = ""  # Confirmation variable for kingdom changes
check_kingdom_at = time.time()  # Check right after start
check_moon_at = check_kingdom_at
check_story_at = check_kingdom_at
kingdom_borders = (161, 27, 211, 77)
moon_borders = (400, 525, 900, 575)
multi_borders = (870, 170, 950, 250)
red_borders = (0, 0, 128, 50)
story_borders = (210, 240, 260, 368)
story_text_borders = (350, 520, 900, 650)
talkatoo_borders = (350, 565, 1000, 615)
text_potential = 0  # So we don't read partial text
old_time = time.time()
stream = cv2.VideoCapture(VIDEO_INDEX)  # Set up capture card
borders = determine_borders(Image.fromarray(cv2.cvtColor(stream.read()[1], cv2.COLOR_BGR2RGB)))  # Find borders to crop every iteration
eel.init('gui')  # Initialize the gui package
eel.start('index.html', port=8083, size=(1920, 1080), block=False)  # start the GUI
print("Setup complete! You may now approach the bird.\n")

while True:
    new_time = time.time()
    frame_time = new_time - old_time
    old_time = new_time
    eel.sleep(0.001)  # sleep of ~0.001 is the minimum allowed, still works

    # Retrieve and resize image
    grabbed, frame = stream.read()
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Resizing image needed for distortion correction. NEAREST is ~8x faster than default but riskier so still testing
    image = Image.fromarray(image[borders[1]:borders[3], borders[0]:borders[2]]).resize((IM_WIDTH, IM_HEIGHT), resample=Image.BICUBIC)

    # Check kingdom every 3s
    if new_time > check_kingdom_at:
        check_kingdom_at = new_time + 3  # Reset timer
        kingdom_check_im = image_to_bw(image.crop(kingdom_borders))  # Must be 50x50 to work in model
        new_kingdom, check_kingdom_in = update_kingdom(kingdom_check_im)
        if new_kingdom and new_kingdom != current_kingdom:  # strong match for new
            if change_kingdom == new_kingdom:  # make sure we get two in a row of the same kingdom
                current_kingdom = new_kingdom
                change_kingdom = ""
                print("Kingdom changed to: ", new_kingdom)
            else:
                change_kingdom = new_kingdom
                check_kingdom_at -= 2  # Perform the second check in 1s to be sure
            continue  # if purple coin logo visible, not getting a moon or talking to talkatoo

    # Moon recognition every half second
    if new_time > check_moon_at:
        check_moon_at = new_time + 0.5  # Reset timer
        moon_check_im = image_to_bw(image.crop(moon_borders), white=230)
        if is_moon(moon_check_im):
            moon_matches = match_moon_text(moon_check_im, prepend="Collected")
            if moon_matches:
                check_moon_at += 5  # Wait 5 extra seconds after a moon
                if moon_matches != collected_moons[-1]:
                    collected_moons.append(moon_matches)
                    continue

    # Story moon recognition every half second
    if new_time > check_story_at:
        check_story_at = new_time + 0.5
        red_check_im = image.crop(red_borders)
        if check_story_multi(red_check_im, expected="RED"):
            story_check_im = image.crop(story_borders)
            if check_story_multi(story_check_im, expected="STORY"):
                print("Got a story moon!", end=" ")
                story_text = image.crop(story_text_borders)
                story_text = image_to_bw(story_text, white=240).rotate(-2.5)
                match_moon_text(story_text, story=True, prepend="Collected")
                check_story_at += 10
                continue
            multi_check_im = image.crop(multi_borders)
            if check_story_multi(multi_check_im, expected="MULTI"):
                print("Got a multi moon!", end="\n")  # Don't bother with OCR since moon border makes it unreliable
                check_story_at += 10
                continue

    # Talkatoo text recognition, every frame
    talkatoo_text, poss_text = talkatoo_preprocess_better(image.crop(talkatoo_borders), current_kingdom)
    if poss_text:
        text_potential += 1
        if text_potential * frame_time > 0.19 and text_potential >= 2 and frame_time <= 0.3:  # Not waiting on a match
            text_potential = 0
            if is_text(talkatoo_text):  # Use text classifier to hopefully avoid unnecessary OCR passes
                moon_matches = match_moon_text(talkatoo_text, prepend="Unlocked")  # Recognize, clean, and match the output string
                if moon_matches:  # Found at least one match
                    if not mentioned_moons or moon_matches != mentioned_moons[-1]:  # Allow nonconsecutive duplicates
                        mentioned_moons.append(moon_matches)
    else:
        text_potential = 0
