"""
This Python script takes the broad approach:
    Retrieve video footage from USB capture card
    Check for possibility of text in a few ways
    Preprocess game feed for better Optical Character Recognition
    Use OCR to look for Talkatoo text in any supported language
    Output the translated version and other close matches
    Check kingdom/moons periodically
"""

import cv2  # pip install opencv-python
import easyocr
import eel  # pip install eel
import json
import numpy as np  # pip install numpy
import os
from PIL import Image  # pip install pillow
import platform
import psutil  # pip install psutil
import time
import torch  # pip install pytorch
import torchvision.transforms as transforms  # should come with pytorch


# parameters that could be set in the gui: capture card resolution, game language, output language, kingdom list (which kingdoms + which order)

reader = easyocr.Reader(["ch_tra"])
TRANSLATE_FROM_TESS = "chi_tra"  # Use Tesseract codes, chi_sim for Simplified Chinese or chi_tra for Traditional Chinese
LANGUAGES = ["english", "chinese_traditional", "chinese_simplified", "japanese", "korean", "dutch", "french_canada",
             "french_france", "german", "italian", "spanish_spain", "spanish_latin_america", "russian"]
TRANSLATE_FROM = "chinese_traditional"  # Language to translate from, moon-list.json keys
TRANSLATE_TO = "english"  # Language you want to translate to, moon-list.json keys

KINGDOM_CERTAINTY = 0.85  # Classifier certainty to prevent uncertain kingdom switches (must occur 2 times in a row)
POSS_MOON_CERTAINTY = 0.1  # Show moon percentage if it's at least 10% possible
SCORE_THRESHOLD = -2  # Score from score_func where a moon can be considered for correctness, -1.5 or 2 is about right
TEXT_CERTAINTY = 0.9  # Classifier certainty that the input is text and not random pixels, usually 0.9 is safe

KINGDOM_TIMER = 3
MOON_TIMER = 0.5
STORY_MOON_TIMER = 0.5

IM_WIDTH = 1280  # Don't change! Testing this way for time save on resizing
IM_HEIGHT = 720  # Don't change! Testing this way for time save on resizing
MIN_TEXT_COUNT = 500  # Number of pixels to count as text, don't change unless moon names aren't seen
VIDEO_INDEX = 0  # Usually capture card is 0, but if you have other video sources it may not be


# Checks recognized text against moons fromm the current kingdom
def check_matches(poss_moon):
    max_corr = -100  # so low it will never matter
    ans = []  # best matches
    poss_matches = {}  # Loose matches
    for i, m in enumerate(moons_by_kingdom[current_kingdom]):  # Loop through moons in the current kingdom
        corr = score_func(m[TRANSLATE_FROM], poss_moon)  # Determine score for moon being compared
        if corr >= SCORE_THRESHOLD:
            poss_matches[m[TRANSLATE_TO]] = corr
            if corr > max_corr:  # Best match so far
                max_corr = corr
                ans = [m]
            elif corr == max_corr:  # Equally good as best match
                ans.append(m)
    poss_matches = score_to_pct(poss_matches)
    return max_corr, ans, poss_matches


def check_matches_story_multi(poss_moon, multi=False):
    story_moons = {"Cap": [], "Cascade": [1], "Sand": [1, 2], "Lake": [], "Wooded": [1, 3], "Lost": [],
                   "Metro": [2, 3, 4, 5, 6], "Snow": [1, 2, 3, 4], "Seaside": [1, 2, 3, 4], "Luncheon": [1, 2, 4],
                   "Bowsers": [1, 2, 3], "Moon": [], "Mushroom": []}
    multi_moons = {"Cap": [], "Cascade": [2], "Sand": [3, 4], "Lake": [1], "Wooded": [2, 4], "Lost": [],
                   "Metro": [1, 7], "Snow": [5], "Seaside": [5], "Luncheon": [3, 5], "Bowsers": [4], "Moon": [],
                   "Mushroom": [33, 34, 35, 36, 37, 38]}
    max_corr = -100  # so low it will never matter
    ans = []  # best matches
    poss_matches = {}  # Loose matches
    if multi:
        moons_to_check = [moons_by_kingdom[current_kingdom][i-1] for i in multi_moons[current_kingdom]]
        moons_to_check.extend(special_multi_moons)
    else:
        moons_to_check = [moons_by_kingdom[current_kingdom][i-1] for i in story_moons[current_kingdom]]

    for i, m in enumerate(moons_to_check):  # Loop through moons in the current kingdom
        i += 1  # SMO moons are 1-indexed
        corr = score_func(m[TRANSLATE_FROM], poss_moon, can_fail_out=False)
        if corr >= max_corr:
            if corr > max_corr:
                max_corr = corr
                ans = [m]
            elif corr == max_corr:
                ans.append(m)
            poss_matches[m[TRANSLATE_TO]] = corr
    poss_matches = score_to_pct(poss_matches, force_match=True)
    return max_corr if max_corr > SCORE_THRESHOLD else SCORE_THRESHOLD, ans, poss_matches


# Very ugly and naive checker for story/multi moon
def check_story_multi(img, expected="RED"):
    if expected == "RED":
        min_red, max_red = 4000, 6400
        min_white, max_white = 0, 0
        min_blue, max_blue = 0, 0
    elif expected == "STORY":
        min_red, max_red = 4350, 4500
        min_white, max_white = 450, 700
        min_blue, max_blue = 450, 700
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


# Expose the auto-recognized collected moons and clear the list (collected moons only need to be updated once)
@eel.expose
def get_collected_moons():
    global collected_moons
    newly_collected_moons = collected_moons
    collected_moons = []
    return newly_collected_moons


# Expose the moons given by talkatoo to the gui
@eel.expose
def get_mentioned_moons():
    return mentioned_moons


# Expose the kingdom moons dictionary to the gui
@eel.expose
def get_moons_by_kingdom():
    return moons_by_kingdom


# Assumes a well preprocessed, black and white image
# Create bounding box for text -> check black pixel density
# Hopefully can find a cleaner way to do this
def is_text_naive(img):
    img_arr = np.array(img)
    black_arr = img_arr[:, :, 0] == 0  # R, G, and B are the same
    black_horiz = np.sum(black_arr, axis=1)
    top_bound, bottom_bound = 0, img.height
    for i, row_sum in enumerate(black_horiz):
        if row_sum > 10:  # found a row with black
            top_bound = i
            break
    if top_bound < 3:
        return False
    for i in range(len(black_horiz)-1, 0, -1):
        if black_horiz[i] > 5:  # found a row with black
            bottom_bound = i
            break
    if bottom_bound >= img.height - 3 or bottom_bound - top_bound < 20:  # not enough whitespace on bottom or too small of a range for text
        return False
    # If not enough black pixels or too many irrational white lines (allowed some, i.e. the character i has white lines)
    if np.max(black_horiz[top_bound:bottom_bound]) < 20 or np.sum(black_horiz[top_bound:bottom_bound] == 0) > 3:
        return False

    black_vert = np.sum(black_arr[top_bound:bottom_bound, :], axis=0)
    left_bound, right_bound = 0, img.width
    for i, col in enumerate(black_vert):
        if col > 10:  # found a column with black
            left_bound = i
            break
    if left_bound < 5:
        return False
    for i in range(len(black_vert)-1, 0, -1):
        if black_vert[i] > 10:  # found a column with black
            right_bound = i
            break
    if right_bound >= img.width - 5 or right_bound - left_bound < 30:  # not enough whitespace on right or too small of a range for text
        return False

    black_count = np.sum(black_vert[left_bound:right_bound])
    total_count = (bottom_bound-top_bound)*(right_bound-left_bound)
    black_pct = black_count/total_count

    if 0.15 < black_pct < 0.75:
        print("Going to OCR ({})".format(black_pct))
        return True
    print("No match ({})".format(black_pct))
    return False
    # return 0.15 < black_pct < 0.75


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
def match_moon_text(moon_img, prepend="Unlocked", story=False, multi=False):
    ocr_text = reader.readtext(np.array(moon_img))
    ocr_text = correct("".join([ocr_text[i][1] for i in range(len(ocr_text))]))
    if len(ocr_text) < 2:
        return None

    if story or multi:
        max_corr, ans, possible = check_matches_story_multi(ocr_text, multi)
        for match in range(len(ans)):
            ans[match]["is_story"] = True
    else:
        max_corr, ans, possible = check_matches(ocr_text)
    if max_corr >= SCORE_THRESHOLD:  # If any reasonable matches, guarantee match if story moon
        best_matches = len(ans)
        if best_matches == 1:
            print("[{}] {} (score={})  ->  {}".format(prepend, ans[0]["english"].upper(), max_corr, possible))
        else:
            print("[{}] {} (score={})  ->  {}".format(prepend, " OR ".join([poss["english"].upper() for poss in ans]), max_corr, possible))
        return ans
    print("\tNo good matches  ->  ".format(possible))
    return None


# Replacement Levenshtein distance cost function
# May not be as effective with English alphabet as spurious character matches will be far more common, and thresholds are different
def score_func(proper_moon, test_moon, can_fail_out=True):
    proper_len = len(proper_moon)
    test_len = len(test_moon)
    len_diff = proper_len - test_len
    if len_diff > 3 and can_fail_out:
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
        if cor - cost <= fail_out and can_fail_out:  # if the score is bad enough then don't bother
            return -10
    return cor - cost


# Translate scores to percent certainty
def score_to_pct(poss_moon_dict, force_match=False):
    if not force_match:
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
        return kingdom_list[result]
    return None  # Was not able to determine kingdom, check in 10 iterations hoping that something's changed


# Read moon translation data
with open("moon-list.json", encoding="utf8") as moon_file:
    moonlist = "".join([line.strip() for line in moon_file.readlines()])
    moonlist = json.loads(moonlist)  # moonlist now a list of dictionaries, one for each moon

# Dictionary to store all moons by kingdom
moons_by_kingdom = {}
special_multi_moons = []  # Ruined/Dark/Darker need to be matched separately
for moon in moonlist:
    this_kingdom = moon["kingdom"]
    this_moon = {"id": moon["id"], "kingdom": moon["kingdom"], TRANSLATE_FROM: moon[TRANSLATE_FROM],
                 TRANSLATE_TO: moon[TRANSLATE_TO], "chinese_simplified": moon["chinese_simplified"]}
    if this_kingdom in moons_by_kingdom:
        moons_by_kingdom[this_kingdom].append(this_moon)
    else:
        moons_by_kingdom[this_kingdom] = [this_moon]
    if this_kingdom in ["Ruined", "Dark Side", "Darker Side"] and moon["id"] == 1:
        special_multi_moons.append(this_moon)

kingdom_list = ("Cap", "Cascade", "Sand", "Lake", "Wooded", "Lost", "Metro", "Seaside",
                "Snow", "Luncheon", "Bowsers", "Moon", "Mushroom")  # to store class values, DO NOT CHANGE ORDER
current_kingdom = kingdom_list[1]  # Start in first kingdom (fine to start in Cap)
mentioned_moons = []  # list of moons mentioned by Talkatoo
collected_moons = []  # list of auto-recognized collected moons

# Load kingdom recognizer
kindom_classifier = torch.jit.load("KingdomModel.zip")  # Pretrained kingdom recognizer, output 0-13 inclusive
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
story_text_borders = (300, 550, 950, 610)
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
        check_kingdom_at = new_time + KINGDOM_TIMER  # Reset timer
        kingdom_check_im = image_to_bw(image.crop(kingdom_borders))  # Must be 50x50 to work in model
        new_kingdom = update_kingdom(kingdom_check_im)
        if new_kingdom and new_kingdom != current_kingdom:  # strong match for new
            if change_kingdom == new_kingdom:  # make sure we get two in a row of the same kingdom
                current_kingdom = new_kingdom
                change_kingdom = ""
                print("Kingdom changed to: ", new_kingdom)
            else:
                change_kingdom = new_kingdom
                check_kingdom_at = new_time + 1  # Perform the second check in 1s to be sure
            continue  # if purple coin logo visible, not getting a moon or talking to talkatoo

    # Moon recognition every half second
    if new_time > check_moon_at:
        moon_check_im = image_to_bw(image.crop(moon_borders), white=230)
        if is_text_naive(moon_check_im):
            moon_matches = match_moon_text(moon_check_im, prepend="Collected")
            if moon_matches:
                check_moon_at = new_time + 6  # 5s tends to be too short so wait 6s
                if not collected_moons or moon_matches != collected_moons[-1]:
                    collected_moons.append(moon_matches)
                    continue
        check_moon_at = new_time + MOON_TIMER  # Reset timer

    # Story moon recognition every half second
    if new_time > check_story_at:
        red_check_im = image.crop(red_borders)
        if check_story_multi(red_check_im, expected="RED"):
            story_check_im = image.crop(story_borders)
            if check_story_multi(story_check_im, expected="STORY"):
                print("Got a story moon!", end=" ")
                story_text = image.rotate(-3).crop(story_text_borders)
                story_text = image_to_bw(story_text, white=240)
                moon_matches = match_moon_text(story_text, story=True, prepend="Collected")
                collected_moons.append(moon_matches)
                check_story_at = new_time + 10
                continue
            multi_check_im = image.crop(multi_borders)
            if check_story_multi(multi_check_im, expected="MULTI"):
                print("Got a multi moon!", end=" ")  # Don't bother with OCR since moon border makes it unreliable
                multi_text = image.rotate(-3).crop(story_text_borders)
                multi_text = image_to_bw(multi_text, white=240)
                moon_matches = match_moon_text(multi_text, multi=True, prepend="Collected")
                collected_moons.append(moon_matches)
                check_story_at = new_time + 10
                continue
        check_story_at = new_time + STORY_MOON_TIMER

    # Talkatoo text recognition, every frame
    talkatoo_text, poss_text = talkatoo_preprocess_better(image.crop(talkatoo_borders), current_kingdom)
    if poss_text:
        text_potential += 1
        if text_potential * frame_time > 0.19 and text_potential >= 2 and frame_time <= 0.3:  # Not waiting on a match
            text_potential = 0
            if is_text_naive(talkatoo_text):  # Use text classifier to hopefully avoid unnecessary OCR passes
                moon_matches = match_moon_text(talkatoo_text, prepend="Unlocked")  # Recognize, clean, and match the output string
                if moon_matches:  # Found at least one match
                    if not mentioned_moons or moon_matches != mentioned_moons[-1]:  # Allow nonconsecutive duplicates
                        mentioned_moons.append(moon_matches)
    else:
        text_potential = 0
