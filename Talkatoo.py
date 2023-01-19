"""
This Python script takes the broad approach:
    Retrieve video footage from USB capture card
    Preprocess game feed for better Optical Character Recognition
    Use OCR to look for Talkatoo text in any supported language
    Print the translated version and other close matches
"""

import cv2  # pip install opencv-python
import json
from PIL import Image  # pip install pillow
import pytesseract  # pip install pytesseract
                    # Then install language files from https://github.com/tesseract-ocr/tessdata and place in tessdata
import time

pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"  # Path to tesseract executable
TRANSLATE_FROM_TESS = "chi_tra"  # Use Pytesseract codes, chi_sim for Simplified Chinese and chi_tra for Traditional Chinese
LANGUAGES = ["english", "chinese_traditional", "chinese_simplified", "japanese", "korean", "dutch", "french_canada",
             "french_france", "german", "italian", "spanish_spain", "spanish_latin_america", "russian"]
TRANSLATE_FROM = "chinese_traditional"  # Language to translate from, moon-list.json keys
TRANSLATE_TO = "english"  # Language you want to translate to, moon-list.json keys

DELAY_CONSTANT = 0.05  # Delays every iteration, used to reduce partial word readings as text scrolls. 0.05 is good here
MIN_TEXT_COUNT = 400  # Number of pixels to count as text, don't change unless short moon names aren't seen
SCORE_THRESHOLD = -2  # Score from score_func where a moon can be considered for correctness
VERBOSE = True  # Prints a lot more information

VIDEO_INDEX = 0  # Usually capture card is 0, but if you have other video sources it may not be
ENLARGE_COEF = 1  # Sometimes enlarging increased accuracy, keep to integer
IM_WIDTH = 1280  # Width of game feed images in pixels
IM_HEIGHT = 720  # Height of game feed images in pixels


# Pseudo-Levenshtein distance cost function
# Note that this implementation does not consider ordering, which is safe enough in Chinese/Japanese
# For languages that use our alphabet, we need a more restrictive/tuned matching system that will be far less efficient
def score_func(s, t):
    s = list(s)
    t = list(t)
    cost = 0
    corr = 0
    for c in s:
        if c in t:  # Character match
            t.remove(c)
            corr += 1
        else:
            cost += 1
    return corr - cost


# Replace certain known problematic characters to make better matches
def correct(string):
    replacements = {" ": "", "，": "‧", ".": "‧", "1": "１", "|": "１", "2": "２", "3": "３", "!": "！"}
    for i in replacements:
        string = string.replace(i, replacements[i])
    return string


# Crops an image to talkatoo text only. Not currently used.
def crop_talkatoo(im):
    min_x, min_y, max_x, max_y = 1000, 1000, 0, 0
    for row in range(0, im.width):
        for col in range(0, im.height):
            if im.getpixel((row, col))[2] < 10:
                if row > max_x:
                    max_x = row
                if row < min_x:
                    min_x = row
                if col > max_y:
                    max_y = col
                if col < min_y:
                    min_y = col
    cropped_talkatoo = im.crop((min_x, min_y, max_x, max_y))
    return cropped_talkatoo


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
        kingdoms[this_kingdom][moon[TRANSLATE_FROM]] = {TRANSLATE_TO: moon[TRANSLATE_TO]}  # Structured for future languages
    else:
        kingdoms[this_kingdom] = {moon[TRANSLATE_FROM]: {TRANSLATE_TO: moon[TRANSLATE_TO]}}  # Structured for future languages
kingdom_list = ["Cap", "Cascade", "Sand", "Lake", "Wooded", "Lost", "Metro", "Snow", "Seaside", "Luncheon", "Bowsers", "Moon", "Mushroom"]
current_kingdom = kingdom_list[1]  # Starting Kingdom
collected_moons = []  # To be updated by JS probably?
talkatoo_moons = {k: [] for k in kingdom_list}  # Dictionary indexed by kingdom to see which moons Talkatoo has given us

# Final setup variables
time_of_last_match = time.time() - 2
x1, y1, x2, y2 = int(200/1280*IM_WIDTH), int(565/720*IM_HEIGHT), int(1000/1280*IM_WIDTH), int(605/720*IM_HEIGHT)
stream = cv2.VideoCapture(VIDEO_INDEX)
print("Setup complete! You may now approach the bird.\n")

# Begin iteration
while True:
    # Retrieve and resize image
    grabbed, frame = stream.read()
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(image)
    talkatoo_text = image.crop((x1, y1, x2, y2))
    talkatoo_text = talkatoo_text.resize(((x2-x1)*ENLARGE_COEF, (y2-y1)*ENLARGE_COEF))  # Enlarging sometimes helps

    # Make yellow pixels black, all else white
    text_count = 0
    total_count = 0
    for row in range(0, talkatoo_text.width):
        for col in range(0, talkatoo_text.height):
            pixel = talkatoo_text.getpixel((row, col))
            if pixel[0] > 200 and pixel[1] > 200 and pixel[2] < 120:  # Note that capture card coloring may vary slightly
                talkatoo_text.putpixel((row, col), (0, 0, 0))
                text_count += 1
            else:
                talkatoo_text.putpixel((row, col), (255, 255, 255))
            total_count += 1

    if text_count < MIN_TEXT_COUNT:  # If there isn't enough text, don't go to OCR step because OCR is very slow
        time.sleep(DELAY_CONSTANT)  # Helps frequent partial-moon readings, can adjust if needed
        continue

    # talkatoo_text.show()  # Show preprocessed text image

    if time.time() - time_of_last_match < 1:  # If too soon after the last one, it's a repeat so skip
        continue

    # Recognize and clean the output string
    data = pytesseract.image_to_string(talkatoo_text, lang=TRANSLATE_FROM_TESS, config='--psm 6')
    data = correct(data.strip())
    if VERBOSE:
        print("Recognized Characters:", data)

    max_corr = -100  # so low it will never matter
    ans = []
    count = 0
    for m in kingdoms[current_kingdom]:  # Loop through moons in the current kingdom
        corr = score_func(m, data)  # Determine score for moon being compared
        if corr > max_corr:  # Best match so far
            max_corr = corr
            ans = [kingdoms[current_kingdom][m][TRANSLATE_TO]]  # English name, in this case
        elif corr == max_corr:  # Equally good as best match
            ans.append(kingdoms[current_kingdom][m][TRANSLATE_TO])  # English name, in this case
        if corr >= SCORE_THRESHOLD - 1:  # Loose match , we don't need this but could situationally be useful
            if VERBOSE:
                print("Possible Match:", kingdoms[current_kingdom][m][TRANSLATE_TO], "(score={})".format(corr))
            count += 1

    if max_corr >= SCORE_THRESHOLD:  # If any reasonable matches
        time_of_last_match = time.time()  # Set up so no duplicates
        if VERBOSE:
            if count == 1:
                print("Possible Match:", count)
            else:
                print("Possible Matches:", count)
        best_matches = len(ans)
        if best_matches == 1:
            print("Best Match:\n\t{} (score={})\n".format(ans, max_corr))
        else:
            print("Best Matches({} total): {} (score={})".format(best_matches, " OR ".join(ans), max_corr))
        talkatoo_moons[current_kingdom].append({ans[0]: False})
