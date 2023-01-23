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
from PIL import Image  # pip install pillow
import pytesseract  # pip install pytesseract
                    # Then install language files from https://github.com/tesseract-ocr/tessdata and place in tessdata
import time
import torch  # pip install pytorch
import torchvision.transforms as transforms  # should come with pytorch


# parameters that could be set in the gui: capture card resolution, game language, output language, kingdom list (which kingdoms + which order)

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"  # Path to tesseract executable
TRANSLATE_FROM_TESS = "chi_tra"  # Use Pytesseract codes, chi_sim for Simplified Chinese and chi_tra for Traditional Chinese
LANGUAGES = ["english", "chinese_traditional", "chinese_simplified", "japanese", "korean", "dutch", "french_canada",
             "french_france", "german", "italian", "spanish_spain", "spanish_latin_america", "russian"]
TRANSLATE_FROM = "chinese_traditional"  # Language to translate from, moon-list.json keys
TRANSLATE_TO = "english"  # Language you want to translate to, moon-list.json keys

CHECK_KINGDOM_EVERY = 100  # Currently iterations are ~0.06s each, and checking kingdom is about 0.006s after in cache
SCORE_THRESHOLD = -2  # Score from score_func where a moon can be considered for correctness
VERBOSE = False  # Prints a lot more information

ENLARGE_COEF = 1  # Sometimes enlarging increased accuracy, keep to integer
IM_WIDTH = 1920  # Width of game feed images in pixels
IM_HEIGHT = 1080  # Height of game feed images in pixels
MIN_TEXT_COUNT = 400  # Number of pixels to count as text, don't change unless short moon names aren't seen
VIDEO_INDEX = 0  # Usually capture card is 0, but if you have other video sources it may not be


# Read JSON data
with open("moon-list.json", encoding="utf8") as moon_file:
    moonlist = "".join([line.strip() for line in moon_file.readlines()])
    moonlist = json.loads(moonlist)  # moonlist now a list of dictionaries, one for each moon

# Dictionary to store all moons by kingdom
# Language indexing as follows: kingdoms["Cap"]["chinese_moon"]["language_name"]
# Collected Boolean as follows: kingdoms["Cap"]["chinese_moon"]["collected"]
kingdoms = {}
for moon in moonlist:
    this_kingdom = moon["kingdom"]
    if this_kingdom in kingdoms:
        kingdoms[this_kingdom].append(moon)
    else:
        kingdoms[this_kingdom] = [moon]

kingdom_list = ["Cap", "Cascade", "Sand", "Lake", "Wooded", "Lost", "Metro", "Seaside",
                "Snow", "Luncheon", "Bowsers", "Moon", "Mushroom"]  # to store class values, DO NOT CHANGE ORDER
active_kingdoms = ["Cascade", "Sand", "Wooded", "Lake", "Lost", "Metro", "Snow", "Seaside", "Luncheon", "Bowsers"]
current_kingdom_idx = 0  # Start in Cascade
current_kingdom = active_kingdoms[current_kingdom_idx]
collected_moons = []  # To be updated by JS probably?
mentioned_moons = []  # list of moons mentioned by talkatoo

# Setup kingdom recognizer
kindom_classifier = torch.jit.load('model.zip')  # Load my model
transform = transforms.PILToTensor()  # Needed to transform image

# Final setup variables
check_kingdom_in = 1  # Start at 1 to check immediately
text_potential = 0  # So we don't read partial text
time_of_last_match = time.time() - 2
x1, y1, x2, y2 = int(200/1280*IM_WIDTH), int(565/720*IM_HEIGHT), int(1000/1280*IM_WIDTH), int(605/720*IM_HEIGHT)
x3, y3, x4, y4 = int(163/1280*IM_WIDTH), int(27/720*IM_HEIGHT), int(213/1280*IM_WIDTH), int(77/720*IM_HEIGHT)
stream = cv2.VideoCapture(VIDEO_INDEX)  # Set up capture card
eel.init('gui')  # Initialize the gui package
eel.start('index.html', port=8083, size=(1920, 1080), block=False)  # start the GUI
print("Setup complete! You may now approach the bird.\n")


def check_matches():
    max_corr = -100  # so low it will never matter
    ans = []
    count = 0
    for m in kingdoms[current_kingdom]:  # Loop through moons in the current kingdom
        corr = score_func(m[TRANSLATE_FROM], data)  # Determine score for moon being compared
        if corr > max_corr:  # Best match so far
            max_corr = corr
            ans = [m]
        elif corr == max_corr:  # Equally good as best match
            ans.append(m)
        if corr >= SCORE_THRESHOLD - 1:  # Loose match, we don't need this but could situationally be useful
            if VERBOSE:
                print("Possible Match:", m[TRANSLATE_TO], "(score={})".format(corr))
            count += 1
    return max_corr, ans, count


# Replace certain known problematic characters to make better matches
def correct(string):
    replacements = {" ": "", "，": "‧", ".": "‧", "1": "１", "|": "１", "2": "２", "3": "３", "!": "！"}
    for i in replacements:
        string = string.replace(i, replacements[i])
    return string


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
    return min_x, min_y, max_x, max_y


# expose the moons given by talkatoo to the gui
@eel.expose
def get_mentioned_moons():
    return mentioned_moons


def kingdom_bw(kingdom_image):
    for row in range(0, kingdom_image.width):
        for col in range(0, kingdom_image.height):
            pixel = kingdom_image.getpixel((row, col))
            if pixel[0] > 240 and pixel[1] > 240 and pixel[2] > 240:  # Note that capture card coloring may vary slightly
                kingdom_image.putpixel((row, col), (0, 0, 0))
            else:
                kingdom_image.putpixel((row, col), (255, 255, 255))
    return kingdom_image


# Pseudo-Levenshtein distance cost function
# Note that this implementation does not consider ordering, which is safe enough in Chinese/Japanese
# For languages that use our alphabet, we need a more restrictive/tuned matching system that will be far less efficient
def score_func(s, t):
    s, t = list(s), list(t)
    cost, cor = 0, 0
    for c in s:
        if c in t:  # Character match
            t.remove(c)
            cor += 1
        else:
            cost += 1
    return cor - cost


def talkatoo_preprocess(img):
    text_count = 0
    total_count = 0
    for row in range(0, img.width):
        for col in range(0, img.height):
            pixel = img.getpixel((row, col))
            if pixel[0] > 200 and pixel[1] > 200 and pixel[2] < 120:  # Note that capture card coloring may vary slightly
                img.putpixel((row, col), (0, 0, 0))
                text_count += 1
            else:
                img.putpixel((row, col), (255, 255, 255))
            total_count += 1
    return img, text_count < MIN_TEXT_COUNT


def update_kingdom(img):
    kc_tensor = transform(img).unsqueeze(dim=0).type(torch.float32)
    result = int(torch.argmax(kindom_classifier(kc_tensor), dim=1))
    if result < 13:  # 13 is "Other" in my model
        new_kingdom = kingdom_list[result]
        return new_kingdom
    return None


# Black borders on the sides of the screen
# Make sure to be in an environment without black fully lining the side/black screen, or this won't work
# Ideally can make a reset button on GUI to rerun this code?
borders = determine_borders(Image.fromarray(cv2.cvtColor(stream.read()[1], cv2.COLOR_BGR2RGB)))
while True:
    # sleep is necessary to run both gui and image processing
    eel.sleep(0.01)  # 0.001 is too little but 0.01 seems to work
    # Retrieve and resize image
    grabbed, frame = stream.read()
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    image = image.crop(borders).resize((IM_WIDTH, IM_HEIGHT))

    check_kingdom_in -= 1
    if check_kingdom_in == 0:
        kingdom_checker = image.crop((x3, y3, x4, y4)).resize((50, 50))
        kingdom_checker = kingdom_bw(kingdom_checker)
        new_kingdom = update_kingdom(kingdom_checker)
        if new_kingdom and new_kingdom != current_kingdom:
            current_kingdom = new_kingdom
            print("Kingdom changed to: ", new_kingdom)
        check_kingdom_in = CHECK_KINGDOM_EVERY

    talkatoo_text = image.crop((x1, y1, x2, y2))
    if ENLARGE_COEF != 1:
        talkatoo_text = talkatoo_text.resize(((x2-x1)*ENLARGE_COEF, (y2-y1)*ENLARGE_COEF))  # Enlarging sometimes helps OCR

    # Make yellow pixels black, all else white
    talkatoo_text, is_no_text = talkatoo_preprocess(talkatoo_text)

    if is_no_text:
        text_potential = 0
        continue
    text_potential += 1
    if text_potential < 3 or time.time() - time_of_last_match < 1:
        continue
    text_potential = 0

    # Recognize and clean the output string
    data = pytesseract.image_to_string(talkatoo_text, lang=TRANSLATE_FROM_TESS, config='--psm 6')
    data = correct(data.strip())
    if VERBOSE:
        print("Recognized Characters:", data, "({})".format(current_kingdom ))

    max_corr, ans, count = check_matches()

    if max_corr >= SCORE_THRESHOLD:  # If any reasonable matches
        time_of_last_match = time.time()  # Set up so no duplicates
        if VERBOSE:
            if count == 1:
                print("Possible Match:", count)
            else:
                print("Possible Matches:", count)
        best_matches = len(ans)
        if best_matches == 1:
            print("Best Match:\n\t{} (score={})\n".format(ans[0]["english"], max_corr))
        else:
            print("Best Matches({} total): {} (score={})".format(best_matches, " OR ".join([poss["english"] for poss in ans]), max_corr))

        if ans[0] not in mentioned_moons:
            mentioned_moons.append(ans[0])
