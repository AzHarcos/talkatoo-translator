"""
This Python script takes the broad approach:
    Retrieve video footage from USB capture card
    Preprocess game feed for better Optical Character Recognition
    Use OCR to look for Talkatoo text in any supported language
    Print the translated version and other close matches
"""

import cv2  # pip install opencv-python
import eel  # pip install eel
import json
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
TRANSLATE_FROM_TESS = "chi_sim"  # Use Tesseract codes, chi_sim for Simplified Chinese or chi_tra for Traditional Chinese
LANGUAGES = ["english", "chinese_traditional", "chinese_simplified", "japanese", "korean", "dutch", "french_canada",
             "french_france", "german", "italian", "spanish_spain", "spanish_latin_america", "russian"]
TRANSLATE_FROM = "chinese_simplified"  # Language to translate from, moon-list.json keys
TRANSLATE_TO = "english"  # Language you want to translate to, moon-list.json keys

CHECK_KINGDOM_EVERY = 80  # Currently iterations are ~0.05s each
KINGDOM_CERTAINTY = 0.85  # Classifier certainty to prevent uncertain kingdom switches
POSS_MOON_CERTAINTY = 0.1  # Show moon if it's at least 10% possible
SCORE_THRESHOLD = -2  # Score from score_func where a moon can be considered for correctness, -1.5 or 2 is about right
TEXT_CERTAINTY = 0.90  # Classifier certainty that the input is text and not random pixels
VERBOSE = False  # Prints a lot more information

IM_WIDTH = 1920  # Width of game feed images in pixels
IM_HEIGHT = 1080  # Height of game feed images in pixels
MIN_TEXT_COUNT = 400  # Number of pixels to count as text, don't change unless short moon names aren't seen
VIDEO_INDEX = 0  # Usually capture card is 0, but if you have other video sources it may not be


# Read moon translation data
with open("moon-list.json", encoding="utf8") as moon_file:
    moonlist = "".join([line.strip() for line in moon_file.readlines()])
    moonlist = json.loads(moonlist)  # moonlist now a list of dictionaries, one for each moon

# Dictionary to store all moons by kingdom
# Language indexing as follows: kingdoms["Cap"]["chinese_moon"]["language_name"]
moons_by_kingdom = {}
for moon in moonlist:
    this_kingdom = moon["kingdom"]
    if this_kingdom in moons_by_kingdom:
        moons_by_kingdom[this_kingdom].append(moon)
    else:
        moons_by_kingdom[this_kingdom] = [moon]

kingdom_list = ["Cap", "Cascade", "Sand", "Lake", "Wooded", "Lost", "Metro", "Seaside",
                "Snow", "Luncheon", "Bowsers", "Moon", "Mushroom"]  # to store class values, DO NOT CHANGE ORDER
active_kingdoms = ["Cascade", "Sand", "Wooded", "Lake", "Lost", "Metro", "Snow", "Seaside", "Luncheon", "Bowsers"]
current_kingdom_idx = 0  # Start in Cascade
current_kingdom = active_kingdoms[current_kingdom_idx]
mentioned_moons = []  # list of moons mentioned by talkatoo

# Load kingdom and text recognizers
kindom_classifier = torch.jit.load("KingdomModel.zip")
text_classifier = torch.jit.load("TextModel.zip")
transform = transforms.PILToTensor()  # Needed to transform image

# Final setup variables
check_kingdom_in = 5  # Check right after start
text_potential = 0  # So we don't read partial text
# time_of_last_match = time.time() - 2
x1, y1, x2, y2 = int(350/1280*IM_WIDTH), int(565/720*IM_HEIGHT), int(1000/1280*IM_WIDTH), int(615/720*IM_HEIGHT)  # For talkatoo text
x3, y3, x4, y4 = int(163/1280*IM_WIDTH), int(27/720*IM_HEIGHT), int(213/1280*IM_WIDTH), int(77/720*IM_HEIGHT)  # For kingdom image
stream = cv2.VideoCapture(VIDEO_INDEX)  # Set up capture card
eel.init('gui')  # Initialize the gui package
eel.start('index.html', port=8083, size=(1920, 1080), block=False)  # start the GUI

# This is to ensure a more reliable runtime, if you tab out then the program runs slower due to caching,
# which can cause performance issues (missed moons)
this_OS = platform.system()
if this_OS == "Windows":
    p = psutil.Process(os.getpid())
    p.nice(psutil.REALTIME_PRIORITY_CLASS)  # For Windows, highest priority
elif this_OS == "Linux" or this_OS == "Darwin":  # Darwin signifies Mac
    p = psutil.Process(os.getpid())
    p.nice(15)  # 20 is max
print("Setup complete! You may now approach the bird.\n")


# Checks recognized text against moons fromm the current kingdom
def check_matches(poss_moon):
    max_corr = -100  # so low it will never matter
    ans = []  # best matches
    poss_matches = {}  # Loose matches
    for m in moons_by_kingdom[current_kingdom]:  # Loop through moons in the current kingdom
        corr = score_func(m[TRANSLATE_FROM], poss_moon)  # Determine score for moon being compared
        if corr > max_corr:  # Best match so far
            max_corr = corr
            ans = [m]
        elif corr == max_corr:  # Equally good as best match
            ans.append(m)
        if corr >= SCORE_THRESHOLD-1:  # Loose match, we don't need this but could situationally be useful
            # print("Possible Match:", m[TRANSLATE_TO], "(score={})".format(corr))
            poss_matches[m[TRANSLATE_TO]] = corr
    poss_matches = score_to_pct(poss_matches)
    return max_corr, ans, poss_matches


# Replace certain known problematic characters to make better matches
def correct(string):
    replacements = {}
    if TRANSLATE_FROM == "chinese_traditional":
        replacements = {" ": "", "，": "‧", ".": "‧", "1": "１", "|": "１", "2": "２", "3": "３", "!": "！", "『": "！",
                        "}": "！", "”": "", "ˋ": "", "\"": "", "'": "", "‵": "", "(": "", ")": ""}
        # for letter in "abdfghklmpqstvwxyzACDEFGHIJKLNOPQRSTUVWXYZ4567890":  # Take off non-"Merci"/"Bonjour"/"MARIO"/1/2/3
        #     replacements[letter] = ""
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
    if max_x - min_x < IM_WIDTH / 2:
        min_x = 0
        max_x = IM_WIDTH - 1
    if max_y - min_y < IM_HEIGHT / 2:
        min_y = 0
        max_y = IM_HEIGHT - 1
    return min_x, min_y, max_x, max_y


# Expose the kingdom moons dictionary to the gui
@eel.expose
def get_moons_by_kingdom():
    return moons_by_kingdom


# Expose the moons given by talkatoo to the gui
@eel.expose
def get_mentioned_moons():
    return mentioned_moons


# Change kingdom recognition image to black and white for better recognition
def kingdom_bw(kingdom_image):
    for row in range(0, kingdom_image.width):
        for col in range(0, kingdom_image.height):
            pixel = kingdom_image.getpixel((row, col))
            if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:  # Note that capture card coloring may vary slightly
                kingdom_image.putpixel((row, col), (0, 0, 0))
            else:
                kingdom_image.putpixel((row, col), (255, 255, 255))
    return kingdom_image


# Checks to see if image is talkatoo text or random pixels
def not_actually_text(img):
    tc_tensor = transform(img).unsqueeze(dim=0).type(torch.float32)
    probs = torch.softmax(text_classifier(tc_tensor), dim=1)
    print(probs)
    if torch.max(probs) < TEXT_CERTAINTY:
        return False
    text_code = torch.argmax(probs)
    return text_code == 1  # 0 means it's text, 1 means it's not


# Replacement Levenshtein distance cost function
# May not be as effective with English alphabet as spurious character matches will be far more common
def score_func(proper_moon, test_moon):
    if len(proper_moon) - len(test_moon) > 3:
        return -10
    fail_out = SCORE_THRESHOLD - 2 - (len(proper_moon) / 4)
    cost = 0
    cor = 0.5 if len(proper_moon) == len(test_moon) else 0  # Give an extra half point if the length is exact
    trav_index = 0
    for c in proper_moon:
        ind = trav_index
        found = False
        while ind < len(test_moon):
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
    cost += max(len(proper_moon) - len(test_moon), 0) / 2  # Penalize missing characters 1.5x as much as the rest
    return cor - cost


def score_to_pct(poss_moon_dict):
    poss_moon_dict["Uncertain"] = SCORE_THRESHOLD
    keys = list(poss_moon_dict.keys())
    percents = torch.softmax(torch.tensor([float(poss_moon_dict[key]) for key in poss_moon_dict]), dim=0)
    return {keys[i]: round(float(percents[i])*100, 2) for i in range(len(keys)) if percents[i] > POSS_MOON_CERTAINTY}


def talkatoo_potential(img):
    r_min = 220
    g_min = 220
    b_max = 120
    text_count = 0
    for row in range(int(3 * img.width / 8), int(5 * img.width / 8)):
        for col in range(int(3 * img.height / 8), int(5 * img.height / 8)):
            pixel = img.getpixel((row, col))
            if pixel[0] > r_min and pixel[1] > g_min and pixel[2] < b_max:  # Note that capture card coloring may vary slightly
                text_count += 1
            if text_count > 200:
                return True
    return False


# Change talkatoo text to black and white, only text, for better OCR
def talkatoo_preprocess(img):
    text_count = 0
    total_count = 0
    if current_kingdom in ["Metro", "Seaside"]:
        r_min, g_min, b_max = 220, 220, 120  # Problem kingdoms
    else:
        r_min, g_min, b_max = 200, 200, 150  # Looser numbers usually work
    for row in range(0, img.width):
        for col in range(0, img.height):
            pixel = img.getpixel((row, col))
            if pixel[0] > r_min and pixel[1] > g_min and pixel[2] < b_max:  # Note that capture card coloring may vary slightly
                img.putpixel((row, col), (0, 0, 0))
                text_count += 1
            else:
                img.putpixel((row, col), (255, 255, 255))
            total_count += 1
    return img, text_count < MIN_TEXT_COUNT


# Check kingdom via recognition and update it if needed
def update_kingdom(img):
    kc_tensor = transform(img).unsqueeze(dim=0).type(torch.float32)
    probs = torch.softmax(kindom_classifier(kc_tensor), dim=1)
    if max(probs[0]) > KINGDOM_CERTAINTY:  # Good option should be 90% certain
        result = int(torch.argmax(probs))
        if result < 13:  # 13 is "Other" in my model
            new_k = kingdom_list[result]
            return new_k, CHECK_KINGDOM_EVERY
    return None, 1


# Remove black borders on the sides of the screen
# Make sure to be in an environment without black fully lining the side/black screen, or this won't work
borders = determine_borders(Image.fromarray(cv2.cvtColor(stream.read()[1], cv2.COLOR_BGR2RGB)))
change_kingdom = ""
old_time = time.time()
while True:
    new_time = time.time()
    frame_time = new_time - old_time
    old_time = new_time
    # print(frame_time)
    # sleep is necessary to run both gui and image processing
    eel.sleep(0.01)  # 0.001 is too little but 0.01 seems to work
    # Retrieve and resize image
    grabbed, frame = stream.read()
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image = image.crop(borders).resize((IM_WIDTH, IM_HEIGHT))

    # Check kingdom on a loop counter, every CHECK_KINGDOM_EVERY iterations
    check_kingdom_in -= 1
    if check_kingdom_in == 0:
        kingdom_checker = image.crop((x3, y3, x4, y4)).resize((50, 50))
        kingdom_checker = kingdom_bw(kingdom_checker)
        new_kingdom, check_kingdom_in = update_kingdom(kingdom_checker)
        if new_kingdom and check_kingdom_in == CHECK_KINGDOM_EVERY and new_kingdom != current_kingdom:  # strong match for new
            if change_kingdom == new_kingdom:  # make sure we get two in a row of the same kingdom
                current_kingdom = new_kingdom
                check_kingdom_in = 20
                change_kingdom = ""
                print("Kingdom changed to: ", new_kingdom)
            else:
                change_kingdom = new_kingdom

    talkatoo_text = image.crop((x1, y1, x2, y2)).resize((650, 50))
    if talkatoo_potential(talkatoo_text):
        # There is potential for text, but we need to wait for it all to appear
        text_potential += 1
        if text_potential * frame_time <= 0.19 or text_potential < 2 or frame_time > 0.3:
            continue
    else:
        text_potential = 0
        continue

    text_potential = 0
    # Make yellow pixels black, all else white
    talkatoo_text, is_no_text = talkatoo_preprocess(talkatoo_text)
    # Use Text Classifier to hopefully avoid unnecessary OCR passes
    if is_no_text or not_actually_text(talkatoo_text):
        continue

    # Recognize and clean the output string
    data = pytesseract.image_to_string(talkatoo_text, lang=TRANSLATE_FROM_TESS, config='--psm 6')
    data = correct(data.strip())
    if len(data) < 3:
        continue

    if VERBOSE:
        print("Recognized Characters:", data, "({})".format(current_kingdom))
        talkatoo_text.show()

    max_corr, ans, possible = check_matches(data)
    print(possible)
    if max_corr >= SCORE_THRESHOLD:  # If any reasonable matches
        best_matches = len(ans)
        if best_matches == 1:
            print("Best Match:\n\t{} (score={})\n".format(ans[0]["english"], max_corr))
        else:
            print("Best Matches({} total): {} (score={})".format(best_matches, " OR ".join([poss["english"] for poss in ans]), max_corr))
        if ans not in mentioned_moons:
            for m in ans:
                m['certainty'] = possible[m[TRANSLATE_TO]]
            mentioned_moons.append(ans)
