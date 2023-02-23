"""
This Python script takes the broad approach:
    Retrieve video footage from USB capture card
    Check for possibility of text in a few ways
    Preprocess game feed for better Optical Character Recognition
    Use OCR to look for Talkatoo text in any supported language
    Output the translated version and other close matches
    Check kingdom/moons/story moons periodically
"""

import cv2  # pip install opencv-python
import easyocr  # pip install easyocr
import eel  # pip install eel
import json
from PIL import Image, ImageGrab  # pip install pillow
from pygrabber.dshow_graph import FilterGraph  # Used for camera inputs
import time
import torch  # pip install pytorch
import torchvision.transforms as transforms
from util_functions import *


# Each language performs best under different thresholds and values
DEFAULTS = {"Text_Lower": 0.15,
            "Text_Upper": 0.75,
            "Text_Height": 20,
            "Score": -2,
            "Moon_Bounds": (400, 525, 900, 575),
            "Talkatoo_Bounds": (350, 565, 1000, 615)
            }
LANGUAGES = {
             "english": dict(DEFAULTS, Language="en"),
             "chinese_traditional": dict(DEFAULTS, Language="ch_tra"),
             "chinese_simplified": dict(DEFAULTS, Language="ch_sim"),
             "japanese": {"Language": "ja", "Text_Lower": 0.12, "Text_Upper": 0.55, "Text_Height": 20, "Score": 2,
                          "Moon_Bounds": (375, 535, 900, 590), "Talkatoo_Bounds": DEFAULTS["Talkatoo_Bounds"]},
             "korean": {"Language": "ko", "Text_Lower": 0.1, "Text_Upper": 0.55, "Text_Height": 20, "Score": 0,
                        "Moon_Bounds": DEFAULTS["Moon_Bounds"], "Talkatoo_Bounds": DEFAULTS["Talkatoo_Bounds"]},
             "dutch": dict(DEFAULTS, Language="nl"),
             "french_canada": dict(DEFAULTS, Language="fr"),
             "french_france": dict(DEFAULTS, Language="fr"),
             "german": dict(DEFAULTS, Language="de"),
             "italian": dict(DEFAULTS, Language="it"),
             "spanish_spain": dict(DEFAULTS, Language="es"),
             "spanish_latin_america": dict(DEFAULTS, Language="es"),
             "russian": {"Language": "ru", "Text_Lower": 0.25, "Text_Upper": 0.75, "Text_Height": 12, "Score": 3,
                         "Moon_Bounds": (250, 535, 1100, 585), "Talkatoo_Bounds": (350, 590, 1000, 640)}
             }

DEFAULT_GAME_LANGUAGE = "chinese_traditional"
DEFAULT_GUI_LANGUAGE = "english"
DEFAULT_VIDEO_INDEX = 0
FULLSCREEN = True  # Fullscreen on Windows
GUI_SIZE = ImageGrab.grab().size if FULLSCREEN else (1280, 720)  # Take screenshot to check screen size
IM_WIDTH = 1280  # This number should not change
IM_HEIGHT = 720  # This number should not change
IMG_PATH = "gui/assets/border_reset_img.png"  # used for GUI checking
SETTINGS_PATH = "gui/assets/settings.json"  # used for persisting settings

# Borders for critical areas, given constant screen size
KINGDOM_BORDERS = (161, 27, 211, 77)
RED_BORDERS = (0, 0, 128, 50)
STORY_BORDERS = (210, 240, 260, 368)
MULTI_BORDERS = (870, 170, 950, 250)
STORY_TEXT_BORDERS = (300, 550, 950, 610)

KINGDOM_TIMER = 3
MOON_TIMER = 0.5
STORY_MOON_TIMER = 0.5

KINGDOM_CERTAINTY = 0.85  # Classifier certainty to prevent uncertain kingdom switches (must occur 2 times in a row)
POSS_MOON_CERTAINTY = 0.1  # Show moon percentage if it's at least 10% possible
RUN_FASTER = False
VERBOSE = True


########################################################################################################################
# Functions that can be called by the JS GUI via eel
########################################################################################################################
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

# Allow the gui to see settings to read from the file
@eel.expose
def get_settings():
    return settings

# Allow the gui to see possible capture cards and names
@eel.expose
def get_video_devices():
    devices = FilterGraph().get_input_devices()
    available_cameras = []
    for device_index, device_name in enumerate(devices):
        available_cameras.append({
            'index': device_index,
            'device_name': device_name,
        })
    return available_cameras

# Allow the gui to overwrite the language to translate from for image recognition
@eel.expose
def set_translate_from(t_from):
    global translate_from, language_settings, reader, score_func
    translate_from = t_from
    language_settings = LANGUAGES[translate_from]
    reader = easyocr.Reader([language_settings["Language"]], verbose=False)
    score_func = score_logogram if translate_from in ["chinese_traditional", "chinese_simplified", "japanese", "korean"] else score_alphabet
    if VERBOSE:
        print("[STATUS] -> translate_from set to {}".format(translate_from))

# Allow the gui to overwrite the language to translate to for logging purposes
@eel.expose
def set_translate_to(t_to):
    global translate_to
    translate_to = t_to
    if VERBOSE:
        print("[STATUS] -> translate_to set to {}".format(translate_to))

# Allow the gui to overwrite the video index
@eel.expose
def set_video_index(new_index):
    global video_index, stream
    stream.release()
    stream.open(new_index)
    updated_borders_image = reset_borders()
    if not updated_borders_image:
        if VERBOSE:
            print("[STATUS] -> video_index could not be set to {}".format(new_index))
        stream.release()
        stream.open(video_index)
        return None
    video_index = new_index
    if VERBOSE:
        print("[STATUS] -> video_index set to {}".format(video_index))
    return updated_borders_image

# Allow the gui to reset the borders of the capture card feed
@eel.expose
def reset_borders():
    global borders
    grabbed, next_frame = stream.read()
    if not grabbed:
        print("[STATUS] -> Could not reset image borders")
        return None
    img_arr = cv2.cvtColor(next_frame, cv2.COLOR_BGR2RGB)
    borders = determine_borders(img_arr)
    if VERBOSE:
        print("[STATUS] -> Reset image borders")
    # Save image so it can be displayed in the GUI
    Image.fromarray(img_arr[borders[1]:borders[3], borders[0]:borders[2]]).resize((IM_WIDTH, IM_HEIGHT)).save(IMG_PATH)
    return IMG_PATH

# Allow the gui to save the current settings to a file
@eel.expose
def write_settings_to_file(settings_string):
    global settings
    with open(SETTINGS_PATH, "w") as settings_file:
        settings_file.write(settings_string)
    settings = json.loads(settings_string)
    if VERBOSE:
        print("[STATUS] -> Saved settings to file!")


########################################################################################################################
# Define Python-only functions
########################################################################################################################
# Checks recognized text against moons fromm the current kingdom
def check_matches(poss_moon, score_threshold, moons_to_check):
    max_corr = score_threshold  # so low it will never matter
    ans = []  # best matches
    poss_matches = {}  # Loose matches
    for i, m in enumerate(moons_to_check):  # Loop through moons in the current kingdom
        corr = score_func(m[translate_from], poss_moon, max_corr)  # Determine score for moon being compared
        if corr >= score_threshold:
            poss_matches[m[translate_to]] = corr
            if corr > max_corr:  # Best match so far
                max_corr = corr
                ans = [m]
            elif corr == max_corr:  # Equally good as best match
                ans.append(m)
        elif corr >= score_threshold - 3 and VERBOSE:
            print("\t-->", m[translate_to], "had score", corr)
    poss_matches = score_to_pct(poss_matches)
    return max_corr, ans, poss_matches


# Checks recognized text against story moons from current kingdom
def check_matches_story_multi(poss_moon, score_threshold, moons_to_check):
    max_corr = -100  # so low it will never matter
    ans = []  # best matches
    poss_matches = {}  # Loose matches
    for i, m in enumerate(moons_to_check, start=1):  # Loop through moons in the current kingdom
        corr = score_func(m[translate_from], poss_moon, score_threshold, can_fail_out=False)
        if corr >= max_corr:
            if corr > max_corr:
                max_corr = corr
                ans = [m]
            elif corr == max_corr:
                ans.append(m)
            poss_matches[m[translate_to]] = corr
    poss_matches = score_to_pct(poss_matches, force_match=True)
    return max_corr if max_corr > score_threshold else score_threshold, ans, poss_matches


# Check USB device list and return matching names
def get_index_for(device_name):
    for device in get_video_devices():
        if device["device_name"] == device_name:
            return device["index"]
    return DEFAULT_VIDEO_INDEX


# Increase priority if run speed is an issue
def increase_priority():
    from os import getpid
    from platform import system
    import psutil  # pip install psutil
    this_OS = system()
    if this_OS == "Windows":
        p = psutil.Process(getpid())
        p.nice(psutil.REALTIME_PRIORITY_CLASS)  # For Windows, highest priority
    elif this_OS == "Linux" or this_OS == "Darwin":  # Darwin signifies Mac
        p = psutil.Process(getpid())
        p.nice(-20)  # -20 is top priority


# Recognize, clean, and check moon text
def match_moon_text(moon_img, moons_to_check, prepend="Unlocked", story_multi=False):
    ocr_text = reader.readtext(moon_img)
    ocr_text = correct_text("".join([ocr_text[i][1] for i in range(len(ocr_text))]), translate_from)
    if VERBOSE:
        print(ocr_text)

    score_thresh = language_settings["Score"]
    if story_multi:
        max_corr, ans, possible = check_matches_story_multi(ocr_text, score_thresh, moons_to_check)
        for match in range(len(ans)):
            ans[match]["is_story"] = True
    else:
        max_corr, ans, possible = check_matches(ocr_text, score_thresh, moons_by_kingdom[current_kingdom])

    if max_corr >= score_thresh:  # If any reasonable matches, guarantee match if story moon
        best_matches = len(ans)
        if VERBOSE:
            if best_matches == 1:
                print("[{}] {} (score={})  ->  {}".format(prepend, ans[0]["english"].upper(), max_corr, possible))
            else:
                print("[{}] {} (score={})  ->  {}".format(prepend, " OR ".join([poss["english"].upper() for poss in ans]), max_corr, possible))
        return ans
    if VERBOSE:
        print("\tNo good matches  ->  ".format(possible))
    return None


# Translate scores to percent certainty
def score_to_pct(poss_moon_dict, force_match=False):
    if not force_match:
        poss_moon_dict["Uncertain"] = language_settings["Score"]
    keys = list(poss_moon_dict.keys())
    percents = torch.softmax(torch.tensor([float(poss_moon_dict[key]) for key in poss_moon_dict]), dim=0)
    return {keys[i]: round(float(percents[i])*100, 2) for i in range(len(keys)) if percents[i] > POSS_MOON_CERTAINTY}


# Get story moons
def story_moons_to_check(multi):
    story_moons = {"Cap": [], "Cascade": [1], "Sand": [1, 2], "Lake": [], "Wooded": [1, 3], "Lost": [],
                   "Metro": [2, 3, 4, 5, 6], "Snow": [1, 2, 3, 4], "Seaside": [1, 2, 3, 4], "Luncheon": [1, 2, 4],
                   "Bowsers": [1, 2, 3], "Moon": [], "Mushroom": []}
    multi_moons = {"Cap": [], "Cascade": [2], "Sand": [3, 4], "Lake": [1], "Wooded": [2, 4], "Lost": [],
                   "Metro": [1, 7], "Snow": [5], "Seaside": [5], "Luncheon": [3, 5], "Bowsers": [4], "Moon": [],
                   "Mushroom": [33, 34, 35, 36, 37, 38]}
    if multi:
        moons_to_check = [moons_by_kingdom[current_kingdom][i-1] for i in multi_moons[current_kingdom]]
        moons_to_check.extend(special_multi_moons)
    else:
        moons_to_check = [moons_by_kingdom[current_kingdom][i-1] for i in story_moons[current_kingdom]]
    return moons_to_check


# Check kingdom via recognition and update it if needed
def update_kingdom(img_arr):
    img = Image.fromarray(img_arr)
    kc_tensor = transform(img).unsqueeze(dim=0).type(torch.float32)
    probs = torch.softmax(kindom_classifier(kc_tensor), dim=1)
    result = int(torch.argmax(probs))
    if result != 13 and probs[0][result] > KINGDOM_CERTAINTY:  # 13 is "Other" in my model
        return kingdom_list[result]
    return None  # Was not able to determine kingdom


########################################################################################################################
# Define variables used for computation
########################################################################################################################
if RUN_FASTER:
    increase_priority()

moons_by_kingdom, special_multi_moons = generate_moon_dict()
kingdom_list = ("Cap", "Cascade", "Sand", "Lake", "Wooded", "Lost", "Metro", "Seaside",
                "Snow", "Luncheon", "Bowsers", "Moon", "Mushroom")  # to store class values, strict order
current_kingdom = "Cap"  # Start in first kingdom (Does not matter what it's initialized to)
mentioned_moons = []  # list of moons mentioned by Talkatoo
collected_moons = []  # list of auto-recognized collected moons

# Load kingdom recognizer
kindom_classifier = torch.jit.load("KingdomModel.zip")  # Pretrained kingdom recognizer, output 0-13 inclusive
transform = transforms.PILToTensor()  # Needed to transform image

# Language setup
settings = read_file_to_json(SETTINGS_PATH)
if settings:
    translate_from = settings["inputLanguage"]
    translate_to = settings["outputLanguage"]
    video_index = get_index_for(settings["videoDevice"]["device_name"])
else:
    translate_from = DEFAULT_GAME_LANGUAGE
    translate_to = DEFAULT_GUI_LANGUAGE
    video_index = DEFAULT_VIDEO_INDEX
language_settings = LANGUAGES[translate_from]
reader = easyocr.Reader([language_settings["Language"]], verbose=False)
score_func = score_logogram if translate_from in ["chinese_traditional", "chinese_simplified", "japanese", "korean"] else score_alphabet

# Set up capture card
stream = cv2.VideoCapture(video_index)  # Set up capture card
borders = None
reset_borders()  # Find borders to crop every iteration

# Final setup variables
change_kingdom = ""  # Confirmation variable for kingdom changes
check_kingdom_at = time.time()  # Check right after start
check_moon_at = time.time()  # Check right after start
check_story_at = time.time()  # Check right after start
old_time = time.time()  # start time for loop
text_potential = 0  # So we don't read partial text

# Set up Eel
eel.init('gui')  # Initialize the gui package
eel.start('index.html', port=8083, size=GUI_SIZE, block=False)  # start the GUI

if VERBOSE:
    print("Setup complete! You may now approach the bird.\n")


########################################################################################################################
# Begin main loop, where all of the detection happens
########################################################################################################################
while True:
    new_time = time.time()
    frame_time = new_time - old_time
    old_time = new_time
    eel.sleep(0.001)  # sleep of ~0.001 is the minimum allowed, still works

    # Retrieve and resize image
    grabbed, frame = stream.read()
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Resizing image needed for distortion correction. NEAREST is ~8x faster than default but riskier so still testing
    image = Image.fromarray(image[borders[1]:borders[3], borders[0]:borders[2]]).resize((IM_WIDTH, IM_HEIGHT))

    # Check kingdom every 3s
    if new_time > check_kingdom_at:
        check_kingdom_at = new_time + KINGDOM_TIMER  # Reset timer
        kingdom_check_im = image_to_bw(image.crop(KINGDOM_BORDERS))  # Must be 50x50 to work in model
        new_kingdom = update_kingdom(kingdom_check_im)
        if new_kingdom and new_kingdom != current_kingdom:  # strong match for new
            if change_kingdom == new_kingdom:  # make sure we get two in a row of the same kingdom
                current_kingdom = new_kingdom
                change_kingdom = ""
                if VERBOSE:
                    print("Kingdom changed to: ", new_kingdom)
            else:
                change_kingdom = new_kingdom
                check_kingdom_at = new_time + 1  # Perform the second check in 1s to be sure
            continue  # if purple coin logo visible, not getting a moon or talking to talkatoo

    # Moon recognition every half second
    if new_time > check_moon_at:
        moon_check_im = image_to_bw(image.crop(language_settings["Moon_Bounds"]), white=230)
        if is_text_naive(moon_check_im, language_settings["Text_Height"], language_settings["Text_Lower"], language_settings["Text_Upper"], VERBOSE):
            moon_matches = match_moon_text(moon_check_im, moons_by_kingdom[current_kingdom], prepend="Collected")
            if moon_matches:
                if not collected_moons or moon_matches != collected_moons[-1]:
                    collected_moons.append(moon_matches)
                    check_moon_at = new_time + 6  # 5s tends to be too short so wait 6s
                    continue
        check_moon_at = new_time + MOON_TIMER  # Reset timer

    # Story moon recognition every half second
    if new_time > check_story_at:
        red_check_im = image.crop(RED_BORDERS)
        if check_story_multi(red_check_im, expected="RED"):
            story_check_im = image.crop(STORY_BORDERS)
            if check_story_multi(story_check_im, expected="STORY"):
                if VERBOSE:
                    print("Got a story moon!", end=" ")
                story_text = image.rotate(-3.5).crop(STORY_TEXT_BORDERS)
                story_text = image_to_bw(story_text, white=240)
                moons_to_check = story_moons_to_check(multi=False)
                moon_matches = match_moon_text(story_text, moons_to_check, prepend="Collected", story_multi=True)
                collected_moons.append(moon_matches)
                check_story_at = new_time + 10
                continue

            multi_check_im = image.crop(MULTI_BORDERS)
            if check_story_multi(multi_check_im, expected="MULTI"):
                if VERBOSE:
                    print("Got a multi moon!", end=" ")  # Don't bother with OCR since moon border makes it unreliable
                multi_text = image.rotate(-3.5).crop(STORY_TEXT_BORDERS)
                multi_text = image_to_bw(multi_text, white=240)
                moons_to_check = story_moons_to_check(multi=True)
                moon_matches = match_moon_text(multi_text, moons_to_check, prepend="Collected", story_multi=True)
                collected_moons.append(moon_matches)
                check_story_at = new_time + 10
                continue

        check_story_at = new_time + STORY_MOON_TIMER

    # Talkatoo text recognition, every frame
    talkatoo_text, poss_text = talkatoo_preprocess_better(image.crop(language_settings["Talkatoo_Bounds"]), current_kingdom)
    if poss_text:
        text_potential += 1
        if text_potential * frame_time > 0.19 and text_potential >= 2 and frame_time <= 0.3:  # Not waiting on a match
            text_potential = 0
            if is_text_naive(talkatoo_text, language_settings["Text_Height"], language_settings["Text_Lower"], language_settings["Text_Upper"], VERBOSE):  # Use text classifier to hopefully avoid unnecessary OCR passes
                moons_to_check = moons_by_kingdom[current_kingdom]
                moon_matches = match_moon_text(talkatoo_text, moons_to_check, prepend="Unlocked")
                if moon_matches:  # Found at least one match
                    if not mentioned_moons or moon_matches != mentioned_moons[-1]:  # Allow nonconsecutive duplicates
                        mentioned_moons.append(moon_matches)
    else:
        text_potential = 0
