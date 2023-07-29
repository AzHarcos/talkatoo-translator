import json
import os
import sys

import numpy as np  # pip install numpy


# Naive checker for story/multi moon
def check_story_multi(img, expected="RED"):
    if expected == "RED":
        min_red, max_red = 4000, 6400
        min_white, max_white = 0, 0
        min_blue, max_blue = 0, 0
    elif expected == "STORY":
        min_red, max_red = 4350, 4600
        min_white, max_white = 425, 700
        min_blue, max_blue = 425, 700
    elif expected == "MULTI":
        min_red, max_red = 4050, 4250
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
def correct_text(string, translate_from):
    if translate_from.startswith("chinese"):  # Designed from
        replacements = {" ": "", "!": "！", "(": "", ";": " ", "@": " ", "1": "１", "2": "２", "3": "３",
                        "4": "４", "5": "５", "6": "６", "7": "７", "8": "８", "9": "９", "0": "０"}
    elif translate_from == "korean":
        replacements = {"3": "3"}
    elif translate_from == "japanese":
        replacements = {}
    elif translate_from == "russian":
        replacements = {" ": "", "<": "", ">": "", "{": "", "}": ""}
    else:
        replacements = {" ": ""}
    for i in replacements:
        string = string.replace(i, replacements[i])
    return string


# Used to set capture card borders, for cropping to work the game must be the whole screen
def determine_borders(img_arr):
    min_x, min_y, max_x, max_y = 0, 0, img_arr.shape[1]-1, img_arr.shape[0]-1
    black_arr = np.sum(img_arr[:, :, :], axis=2) >= 20  # im.width by im.height array of True/False
    black_horiz = np.sum(black_arr, axis=1)  # row sums
    black_vert = np.sum(black_arr, axis=0)  # column sums
    for i, over_thresh in enumerate(black_vert):
        if over_thresh:  # If any pixel in col is over threshold
            min_x = i
            break
    for i in range(max_x, 0, -1):
        if black_vert[i]:  # If any pixel in col is over threshold
            max_x = i
            break
    for i, over_thresh in enumerate(black_horiz):
        if over_thresh:  # If any pixel in row is over threshold
            min_y = i
            break
    for i in range(max_y, 0, -1):
        if black_horiz[i]:  # If any pixel in row is over threshold
            max_y = i
            break
    # Defaults
    if max_x - min_x < img_arr.shape[1] / 2:
        min_x, max_x = 0, img_arr.shape[1] - 1
    if max_y - min_y < img_arr.shape[0] / 2:
        min_y, max_y = 0, img_arr.shape[0] - 1
    return min_x, min_y, max_x, max_y


def generate_moon_dict():
    # Read moon translation data
    moonlist = read_file_to_json("moon-list.json")  # moonlist now a list of dictionaries, one for each moon
    # Dictionary to store all moons by kingdom
    moons_by_kingdom = {}
    hint_arts = {}
    for moon in moonlist:
        ha_kingdom = moon.get("collection_kingdom")
        if ha_kingdom:
            if ha_kingdom in hint_arts:
                hint_arts[ha_kingdom].append(moon)
            else:
                hint_arts[ha_kingdom] = [moon]
                
        this_kingdom = moon["kingdom"]
        if this_kingdom in moons_by_kingdom:
            moons_by_kingdom[this_kingdom].append(moon)
        else:
            moons_by_kingdom[this_kingdom] = [moon]
    return moons_by_kingdom, hint_arts


# Make black and white image of purple coin counter and moon text
def image_to_bw(img, white=240):
    image_arr = np.array(img)
    red = image_arr[:, :, 0] <= white
    green = image_arr[:, :, 1] <= white
    blue = image_arr[:, :, 2] <= white
    image_arr[:, :, 0] = np.maximum.reduce([red, green, blue]) * 255  # if any untrue make white, else black
    image_arr[:, :, 1] = image_arr[:, :, 2] = image_arr[:, :, 0]
    return image_arr.astype(np.uint8)


# Assumes a well preprocessed, black and white image
# Create bounding box for text -> check black pixel density
def is_text_naive(img_arr, text_height, text_lower, text_upper, verbose):
    black_arr = img_arr[:, :, 0] == 0  # R, G, and B are the same
    thresh_x, thresh_y = 20, 10

    black_horiz = np.sum(black_arr, axis=1)
    black_horiz_bool = black_horiz > thresh_x
    top_bound = np.argmax(black_horiz_bool)
    if top_bound < 3 or top_bound > 30:  # Not enough whitespace on top
        return False
    bottom_bound = img_arr.shape[0] - np.argmax(black_horiz_bool[::-1]) - 1
    if bottom_bound >= len(black_horiz_bool) - 3 or bottom_bound - top_bound < text_height:  # not enough whitespace on bottom or too small of a range for text
        return False
    # If not enough black pixels or too many irrational white lines (allowed some, i.e. the character i has white lines)
    if np.max(black_horiz[top_bound:bottom_bound]) < 20 or np.sum(black_horiz[top_bound:bottom_bound] == False) > 3:
        return False

    black_vert = np.sum(black_arr[top_bound:bottom_bound, :], axis=0)
    black_vert_bool = black_vert > thresh_y
    left_bound = np.argmax(black_vert_bool)
    if left_bound < 5:  # Not enough whitespace on left
        return False
    right_bound = img_arr.shape[1] - np.argmax(black_vert_bool[::-1]) - 1
    if right_bound >= len(black_vert_bool) - 5 or right_bound - left_bound < 30:  # not enough whitespace on right or too small of a range for text
        return False

    black_pct = np.sum(black_vert[left_bound:right_bound]) / ((bottom_bound-top_bound)*(right_bound-left_bound))
    if text_lower < black_pct < text_upper:
        if verbose:
            print("Going to OCR ({}) -> ".format(black_pct), end="")
        return True
    if verbose:
        print("No match ({}) -> ".format(black_pct))
    return False


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def read_file_to_json(path):
    full_path = resource_path(path)
    try:
        with open(full_path, encoding="utf8") as file:
            json_str = "".join([line.strip() for line in file.readlines()])
        return json.loads(json_str)
    except FileNotFoundError:
        return None


# Replacement Levenshtein distance cost function, designed for alphabet-based languages
# Basis is few missing characters
def score_alphabet(proper_moon, test_moon, low_point, can_fail_out=True):
    proper_moon = proper_moon.replace(" ", "")
    proper_len = len(proper_moon)
    test_len = len(test_moon)
    len_diff = proper_len - test_len
    best_score = -10
    fail_out = low_point - 2 - (proper_len / 4)

    if len_diff < 0:
        longer_moon = test_moon
        shorter_moon = proper_moon
    else:
        longer_moon = proper_moon
        shorter_moon = test_moon

    # Loop through, check comparison at each possible index
    for i in range(abs(len_diff) + 1):
        this_score = 0
        for j, c in enumerate(shorter_moon):
            if c == longer_moon[i+j]:
                this_score += 1
            else:
                this_score -= 1
            if this_score < fail_out and can_fail_out:
                break
        if this_score > best_score:
            best_score = this_score
    return best_score


# Replacement Levenshtein distance cost function, good for Asian languages
# Basis is shared characters, order is less important
def score_logogram(proper_moon, test_moon, low_point, can_fail_out=True):
    proper_len = len(proper_moon)
    test_len = len(test_moon)
    len_diff = proper_len - test_len
    if len_diff > 3 and can_fail_out:
        return -10
    fail_out = low_point - 2 - (proper_len / 4)
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
        if cor - cost <= fail_out and can_fail_out:  # if the score is bad enough then don't bother continuing
            return -10
    return cor - cost


# Preprocess talkatoo text box, yellow text becomes black while all else becomes white
def talkatoo_preprocess_better(talk_img, kingd, min_text=500):
    image_arr = np.array(talk_img)
    if kingd in ["Metro", "Seaside"]:
        r_min, g_min, b_max = 220, 220, 120  # Problem kingdoms
    elif kingd in ["Sand"]:
        r_min, g_min, b_max = 210, 210, 140  # Middle kingdoms
    else:
        r_min, g_min, b_max = 200, 200, 150  # Looser numbers usually work
    red = image_arr[:, :, 0] <= r_min
    green = image_arr[:, :, 1] <= g_min
    blue = image_arr[:, :, 2] >= b_max
    image_arr[:, :, 0] = np.maximum.reduce([red, green, blue]) * 255  # if any untrue make white, else black
    image_arr[:, :, 1] = image_arr[:, :, 2] = image_arr[:, :, 0]
    text_count = np.sum(image_arr[:, :, 0] == 0)
    return image_arr.astype(np.uint8), text_count > min_text
