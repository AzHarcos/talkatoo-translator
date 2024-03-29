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
from json import dumps
from PIL import Image, ImageGrab  # pip install pillow
import platform
import pyaudio
from pygrabber.dshow_graph import FilterGraph  # pip install pygrabber
import threading
import time
import torch  # pip install torch
import torchvision.transforms as transforms
from util_functions import *
from window_capture import *
import warnings
warnings.filterwarnings('ignore')


# Each language performs best under different thresholds and values
ASIAN_MOON_BOUNDS = (300, 525, 950, 575)
DEFAULT_MOON_BOUNDS = (250, 535, 1100, 585)
JAPANESE_MOON_BOUNDS = (375, 535, 900, 590)

ASIAN_TALKATOO_BOUNDS = (350, 565, 1000, 615)  # Line 1 of 1
DEFAULT_TALKATOO_BOUNDS_2 = (350, 590, 1000, 640)  # Line 2 of 2
DEFAULT_TALKATOO_BOUNDS_3 = (350, 610, 1000, 660)  # Line 3 of 3
TALKATOO_BOUNDS_FR = (300, 565, 900, 615)  # Line 1 of 1
TALKATOO_BOUNDS_NL = (350, 560, 1000, 620)  # Line 2 of 3
TALKATOO_BOUNDS_ES = (350, 565, 1000, 615)  # Line 1 of 1

LANGUAGES = {
             "english": {"Language": "en", "Text_Lower": 0.12, "Text_Upper": 0.55, "Text_Height": 12, "Score": 0,
                         "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": DEFAULT_TALKATOO_BOUNDS_2},
             "chinese_traditional": {"Language": "ch_tra", "Text_Lower": 0.15, "Text_Upper": 0.75, "Text_Height": 20,
                                     "Score": -2, "Moon_Bounds": ASIAN_MOON_BOUNDS, "Talkatoo_Bounds": ASIAN_TALKATOO_BOUNDS},
             "chinese_simplified": {"Language": "ch_sim", "Text_Lower": 0.15, "Text_Upper": 0.75, "Text_Height": 20,
                                    "Score": -2, "Moon_Bounds": ASIAN_MOON_BOUNDS, "Talkatoo_Bounds": ASIAN_TALKATOO_BOUNDS},
             "japanese": {"Language": "ja", "Text_Lower": 0.12, "Text_Upper": 0.55, "Text_Height": 20, "Score": 2,
                          "Moon_Bounds": JAPANESE_MOON_BOUNDS, "Talkatoo_Bounds": ASIAN_TALKATOO_BOUNDS},
             "korean": {"Language": "ko", "Text_Lower": 0.1, "Text_Upper": 0.55, "Text_Height": 20, "Score": 0,
                        "Moon_Bounds": ASIAN_MOON_BOUNDS, "Talkatoo_Bounds": ASIAN_TALKATOO_BOUNDS},
             "dutch": {"Language": "nl", "Text_Lower": 0.15, "Text_Upper": 0.55, "Text_Height": 12, "Score": 2,
                       "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": TALKATOO_BOUNDS_NL},
             "french_canada": {"Language": "fr", "Text_Lower": 0.15, "Text_Upper": 0.55, "Text_Height": 12, "Score": 2,
                               "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": TALKATOO_BOUNDS_FR},
             "french_france": {"Language": "fr", "Text_Lower": 0.15, "Text_Upper": 0.55, "Text_Height": 12, "Score": 2,
                               "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": TALKATOO_BOUNDS_FR},
             "german": {"Language": "de", "Text_Lower": 0.15, "Text_Upper": 0.55, "Text_Height": 12,
                        "Score": 2, "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": DEFAULT_TALKATOO_BOUNDS_3},
             "italian": {"Language": "it", "Text_Lower": 0.12, "Text_Upper": 0.55, "Text_Height": 12, "Score": 0,
                         "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": DEFAULT_TALKATOO_BOUNDS_2},
             "spanish_spain": {"Language": "es", "Text_Lower": 0.15, "Text_Upper": 0.55, "Text_Height": 12, "Score": 2,
                               "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": TALKATOO_BOUNDS_ES},
             "spanish_latin_america": {"Language": "es", "Text_Lower": 0.15, "Text_Upper": 0.55, "Text_Height": 12, "Score": 2,
                                       "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": DEFAULT_TALKATOO_BOUNDS_3},
             "russian": {"Language": "ru", "Text_Lower": 0.12, "Text_Upper": 0.55, "Text_Height": 12, "Score": 0,
                         "Moon_Bounds": DEFAULT_MOON_BOUNDS, "Talkatoo_Bounds": DEFAULT_TALKATOO_BOUNDS_2}
             }

DEFAULT_GAME_LANGUAGE = "chinese_traditional"
DEFAULT_GUI_LANGUAGE = "english"
DEFAULT_AUDIO_INDEX = 0
DEFAULT_VIDEO_INDEX = 0
FULLSCREEN = True  # Fullscreen on Windows
GUI_SIZE = ImageGrab.grab().size if FULLSCREEN else (1280, 720)  # Take screenshot to check screen size
IM_WIDTH = 1280  # This number should not change
IM_HEIGHT = 720  # This number should not change
IMG_PATH = "gui/assets/border_reset_img.png"  # used for GUI checking
SETTINGS_PATH = "settings.json"  # used for persisting settings
PENDING_MOONS_PATH = "pending-moons.txt" # can be used to display pending moons in OBS

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
VERBOSE = True

MAX_STORY = {"Cap": 0, "Cascade": 2, "Sand": 4, "Lake": 1, "Wooded": 4, "Cloud": 0, "Lost": 0, "Metro": 7,
             "Snow": 5, "Seaside": 5, "Luncheon": 5, "Ruined": 1, "Bowsers": 4, "Moon": 0, "Mushroom": 38,
             "Dark": 1, "Darker": 1}
MAX_MAINGAME = {"Cap": 0, "Cascade": 25, "Sand": 69, "Lake": 33, "Wooded": 54, "Cloud": 0, "Lost": 25, "Metro": 66,
                "Snow": 37, "Seaside": 52, "Luncheon": 56, "Ruined": 5, "Bowsers": 45, "Moon": 27, "Mushroom": 0,
                "Dark": 0, "Darker": 0}


########################################################################################################################
# Functions that can be called by the JS GUI via eel
########################################################################################################################

# Expose the kingdom moons dictionary to the gui
@eel.expose
def get_moons_by_kingdom():
    return moons_by_kingdom

# Allow the gui to request the list of currently open windows
@eel.expose
def get_open_windows():
    return list_open_windows()

# Allow the gui to see settings to read from the file
@eel.expose
def get_settings():
    return settings

# Allow the gui to check if the video stream is playing
@eel.expose
def is_video_playing():
    return output_video

# Allow the gui to check if audio is playing
@eel.expose
def is_audio_playing():
    return output_audio

# Allow the gui to see possible audio devices
@eel.expose
def get_audio_devices():
    available_devices = []
    for i in range(0, p.get_host_api_info_by_index(0).get('deviceCount')):
        if (p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) >= 2:
            available_devices.append({"index": i,
                                      "device_name": p.get_device_info_by_host_api_device_index(0, i).get('name')})
    return available_devices

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

# Allow the gui to set the current kingdom
@eel.expose
def set_current_kingdom(kingdom_name):
    global current_kingdom

    if kingdom_name in kingdom_list:
        current_kingdom = kingdom_name
        eel.set_current_kingdom(current_kingdom)
        if VERBOSE:
            print("Kingdom changed to: ", kingdom_name)


# Allow the gui to reset the borders of the capture card feed
@eel.expose
def reset_borders(window_hwnd=None):
    global window_stream

    if window_hwnd is not None:
        window_stream = WindowCapture(window_hwnd, window_capture_cropping)

    new_borders, img_arr = reset_capture_borders()
    if not new_borders:
        return None
    # Save image so it can be displayed in the GUI
    path = internal_resource_path(IMG_PATH)

    # Draw lines around story text
    preview_img = np.array(Image.fromarray(img_arr[borders[1]:borders[3], borders[0]:borders[2]]).resize((IM_WIDTH, IM_HEIGHT)))
    rotated_img = np.array(Image.fromarray(preview_img).rotate(-3.5))
    mask = np.zeros((STORY_TEXT_BORDERS[3] - STORY_TEXT_BORDERS[1], STORY_TEXT_BORDERS[2] - STORY_TEXT_BORDERS[0]), dtype=bool)
    mask[0] = mask[:, 0] = mask[-1] = mask[:, -1] = True
    rotated_img[STORY_TEXT_BORDERS[1]:STORY_TEXT_BORDERS[3], STORY_TEXT_BORDERS[0]:STORY_TEXT_BORDERS[2]][mask] = np.array([0, 255, 0])  # Green
    rotated_img = np.array(Image.fromarray(rotated_img).rotate(3.5))
    preview_img[50:-50, 50:-50] = rotated_img[50:-50, 50:-50]

    # Draw lines around purple coin counter, moon text, and talkatoo text
    colors = [np.array([255, 165, 0]), np.array([255, 0, 0]), np.array([255, 165, 0])]
    for i, curr_borders in enumerate([KINGDOM_BORDERS, language_settings["Moon_Bounds"], language_settings["Talkatoo_Bounds"]]):
        mask = np.zeros((curr_borders[3]-curr_borders[1], curr_borders[2]-curr_borders[0]), dtype=bool)
        mask[0] = mask[:, 0] = mask[-1] = mask[:, -1] = True
        preview_img[curr_borders[1]:curr_borders[3], curr_borders[0]:curr_borders[2]][mask] = colors[i]
    Image.fromarray(preview_img).save(path)
    return path

# Allow the gui to reset the run, in this case clearing the mentioned and collected moons
@eel.expose
def reset_run(skip_reset_confirmation):
    global mentioned_moons, collected_moons
    mentioned_moons = []
    collected_moons = []
    if VERBOSE:
        print("[STATUS] -> reset moon lists")
    if skip_reset_confirmation:
        updated_settings = settings
        updated_settings["skipResetConfirmation"] = True
        return write_settings_to_file(updated_settings)
    return True

# Allow eel to ruin everything
@eel.expose
def shutdown():
    global running
    print("Shutdown initiated")
    running = False

# Allow GUI to start video
@eel.expose
def start_output_video():
    global output_video
    output_video = True
    print("[STATUS] -> started video output")
    return True

# Allow GUI to stop video
@eel.expose
def stop_output_video():
    global output_video
    output_video = False
    print("[STATUS] -> stopped video output")
    return True

# Allow GUI to start audio
@eel.expose
def start_output_audio():
    global output_audio
    output_audio = True
    print("[STATUS] -> started audio output")
    return True

# Allow GUI to stop audio
@eel.expose
def stop_output_audio():
    global output_audio
    output_audio = False
    print("[STATUS] -> stopped audio output")
    return True

# Allow the gui to save the current settings to a file
@eel.expose
def write_settings_to_file(updated_settings):
    global settings, is_postgame, translate_from, translate_to, include_extra_kingdoms, manually_switch_kingdoms, use_window_capture, window_capture_cropping, output_video, output_audio, audio_index

    if updated_settings["useWindowCapture"]:
        if not set_window_capture(updated_settings["windowCaptureName"]):
            return False
    elif updated_settings["videoDevice"] is not None:
        if not set_video_index(updated_settings["videoDevice"]["index"]):
            return False

    if updated_settings["audioDevice"] is not None:
        audio_index = updated_settings["audioDevice"]["index"]

    if not set_use_window_capture(updated_settings["useWindowCapture"]):
        return False
    if not set_window_capture_cropping(updated_settings["windowCaptureCropping"]):
        return False

    is_postgame = updated_settings["includePostGame"]
    include_extra_kingdoms = updated_settings["includeWithoutTalkatoo"]
    set_translate_from(updated_settings["inputLanguage"])
    set_translate_to(updated_settings["outputLanguage"])
    manually_switch_kingdoms = updated_settings.get("manuallySwitchKingdoms", False)

    with open(SETTINGS_PATH, "w+") as settings_file:
        settings_file.write(dumps(updated_settings))
    if VERBOSE:
        print("[STATUS] -> Saved settings to file!")
    settings = read_file_to_json(SETTINGS_PATH)
    return True

# Allow the gui to write the pending moons of the selected kingdom to a file
@eel.expose
def log_pending_moons(pending_moons):
    with open(PENDING_MOONS_PATH, "w+", encoding="utf-8") as pending_moons_log_file:
        pending_moons_log_file.write(pending_moons)


########################################################################################################################
# Define Python-only functions
########################################################################################################################
# Checks recognized text against moons fromm the current kingdom
def check_matches(poss_moon, score_threshold, moons_to_check):
    max_corr = score_threshold  # so low it will never matter
    max_low = score_threshold + 4  # Used for shortcutting when scores are blown up
    ans = []  # best matches
    poss_matches = {}  # Loose matches
    for i, m in enumerate(moons_to_check):  # Loop through moons in the current kingdom
        corr = score_func(m[translate_from], poss_moon, max_corr if max_corr < max_low else max_low)  # Determine score for moon being compared
        if corr >= score_threshold:
            poss_matches[m[translate_to]] = corr
            if corr > max_corr:  # Best match so far
                max_corr = corr
                ans = [m]
            elif corr == max_corr:  # Equally good as best match
                ans.append(m)
        elif corr >= score_threshold - 1 and VERBOSE:
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
        if corr > max_corr:
            max_corr = corr
            ans = [m]
        elif corr == max_corr:
            ans.append(m)
        if corr >= score_threshold - 6:
            poss_matches[m[translate_to]] = corr
    poss_matches = score_to_pct(poss_matches, force_match=True)
    return max_corr if max_corr > score_threshold else score_threshold, ans, poss_matches


# Check USB device list and return matching names
def get_index_for(device_name):
    for device in get_video_devices():
        if device["device_name"] == device_name:
            return device["index"]
    return DEFAULT_VIDEO_INDEX


# Recognize, clean, and check moon text
def match_moon_text(moon_img, prepend="Unlocked", story=False, multi=False):
    ocr_text = reader.readtext(moon_img)
    ocr_text = correct_text("".join([ocr_text[i][1] for i in range(len(ocr_text))]), translate_from)
    if len(ocr_text) < 2:
        return None
    if VERBOSE:
        print(ocr_text)

    score_thresh = language_settings["Score"]
    if story:
        to_check = story_moons_to_check(multi=False)
        max_corr, ans, possible = check_matches_story_multi(ocr_text, score_thresh, to_check)
    elif multi:
        to_check = story_moons_to_check(multi=True)
        max_corr, ans, possible = check_matches_story_multi(ocr_text, score_thresh, to_check)
    else:
        to_check = normal_moons_to_check(prepend == "Unlocked")
        max_corr, ans, possible = check_matches(ocr_text, score_thresh, to_check)

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


# Get normal moons
def normal_moons_to_check(is_talkatoo):
    # Note that MAX dicts are 1-indexed as SMO moons are 1-indexed
    if is_postgame:
        if current_kingdom == "Mushroom":
            if is_talkatoo:
                to_check = moons_by_kingdom["Mushroom"][:32] + moons_by_kingdom["Mushroom"][38:43]
            else:
                to_check = moons_by_kingdom["Mushroom"][:32] + moons_by_kingdom["Mushroom"][38:]
        else:
            to_check = moons_by_kingdom[current_kingdom][MAX_STORY[current_kingdom]:]
        if not is_talkatoo: # add cloud, ruined and dark moons for moon get text only
            to_check.extend(moons_by_kingdom["Cloud"])
            to_check.extend(moons_by_kingdom["Ruined"])
            to_check.extend(moons_by_kingdom["Dark"][1:14])  # Exclude multi moon, hint arts already included
    else:
        to_check = moons_by_kingdom[current_kingdom][MAX_STORY[current_kingdom]: MAX_MAINGAME[current_kingdom]]
    to_check.extend(hint_arts[current_kingdom])
    return to_check


# Get story moons
def story_moons_to_check(multi):
    start_index = 33 if current_kingdom == "Mushroom" else 1  # Moon indices are 1-indexed
    if multi:
        moons_to_check = [moons_by_kingdom[current_kingdom][i] for i in range(start_index-1, MAX_STORY[current_kingdom]) if moons_by_kingdom[current_kingdom][i].get("is_multi")]
        moons_to_check.append(moons_by_kingdom["Ruined"][0])
        if is_postgame:
            moons_to_check.append(moons_by_kingdom["Dark"][0])
            moons_to_check.append(moons_by_kingdom["Darker"][0])
    else:
        moons_to_check = [moons_by_kingdom[current_kingdom][i] for i in range(start_index-1, MAX_STORY[current_kingdom]) if moons_by_kingdom[current_kingdom][i].get("is_story")]
    return moons_to_check


# Translate scores to percent certainty
def score_to_pct(poss_moon_dict, force_match=False):
    if not force_match:
        poss_moon_dict["Uncertain"] = language_settings["Score"]
    keys = list(poss_moon_dict.keys())
    percents = torch.softmax(torch.tensor([float(poss_moon_dict[key]) for key in poss_moon_dict]), dim=0)
    return {keys[i]: round(float(percents[i])*100, 2) for i in range(len(keys)) if percents[i] > POSS_MOON_CERTAINTY}


# reset input language
def set_translate_from(t_from):
    global translate_from, language_settings, reader, score_func
    if translate_from != t_from:
        translate_from = t_from
        language_settings = LANGUAGES[translate_from]
        reader = easyocr.Reader([language_settings["Language"]], verbose=False)
        score_func = score_logogram if translate_from in ["chinese_traditional", "chinese_simplified", "japanese", "korean"] else score_alphabet
        if VERBOSE:
            print("[STATUS] -> translate_from set to {}".format(translate_from))


# reset output language
def set_translate_to(t_to):
    global translate_to
    if translate_to != t_to:
        translate_to = t_to
        if VERBOSE:
            print("[STATUS] -> translate_to set to {}".format(translate_to))


# reset video source
def set_video_index(new_index):
    global video_index, stream

    if video_index == new_index:
        return True

    stream.release()
    stream.open(new_index)
    reset_success = reset_borders()
    if reset_success:
        video_index = new_index
        if VERBOSE:
            print("[STATUS] -> video_index set to {}".format(video_index))
        return True
    else:
        if VERBOSE:
            print("[STATUS] -> video_index could not be set to {}".format(new_index))
        stream.release()
        stream.open(video_index)
        return False


# reset window capture
def set_window_capture(window_name, force_update=False):
    global this_OS, use_window_capture, window_capture_name, window_stream

    if not force_update and window_capture_name == window_name:
        return True

    if this_OS == "Windows":
        if window_name is None:
            window_capture_name = None
            window_stream = WindowCapture(None, window_capture_cropping)
            reset_borders()
            return True

        current_stream = window_stream
        windows = list_open_windows()
        windows = [window for window in windows if window_name == window["name"]]
        if windows:
            target_window = windows[0]
            window_capture_name = target_window["name"]
            reset_success = reset_borders(target_window["hwnd"])
            if reset_success:
                if VERBOSE:
                    print("[STATUS] -> Started window capture for {}".format(window_name))
                return True
        if VERBOSE:
            print("[STATUS] -> Could not start window capture for {}, make sure the window is not minimized.".format(window_name))
        window_stream = WindowCapture(None) if current_stream is None else current_stream
        return False
    else:
        print("[STATUS] -> Window capture is only supported on Windows OS.")
    return False


# switch between video device and window capture
def set_use_window_capture(_use_window_capture):
    global this_OS, use_window_capture, window_capture_name

    if this_OS != "Windows" and _use_window_capture:
        print("[STATUS] -> Window capture is only supported on Windows OS.")
        return False

    if use_window_capture == _use_window_capture:
        return True

    use_window_capture = _use_window_capture
    if use_window_capture:
        print("[STATUS] -> Switched to window capture.")
        return set_window_capture(window_capture_name, True)
    else:
        print("[STATUS] -> Switched to video device.")
        return reset_borders()


# set the cropping values for the window capture
def set_window_capture_cropping(updated_cropping):
    global window_capture_cropping

    current_cropping = window_capture_cropping
    window_capture_cropping = updated_cropping

    success = set_window_capture(window_capture_name, True)

    if not success:
        window_capture_cropping = current_cropping

    return success


# Check kingdom via recognition and update it if needed
def update_kingdom(img_arr):
    img = Image.fromarray(img_arr)
    kc_tensor = transform(img).unsqueeze(dim=0).type(torch.float32)
    probs = torch.softmax(kindom_classifier(kc_tensor), dim=1)
    result = int(torch.argmax(probs))
    if result != 13 and probs[0][result] > KINGDOM_CERTAINTY:  # 13 is "Other" in my model
        return kingdom_list[result]
    return None  # Was not able to determine kingdom


# Reset capture card borders
def reset_capture_borders():
    global borders
    if use_window_capture:
        next_frame = window_stream.get_screenshot()
        grabbed = next_frame is not None and next_frame.size > 0
    else:
        grabbed, next_frame = stream.read()

    if not grabbed:
        print("[STATUS] -> Could not reset image borders")
        return None, None

    img_arr = cv2.cvtColor(next_frame, cv2.COLOR_BGR2RGB)
    if use_window_capture:
        borders = (0, 0, img_arr.shape[1], img_arr.shape[0])
    else:
        borders = determine_borders(img_arr)

    if VERBOSE:
        print("[STATUS] -> Reset image borders")
    return borders, img_arr


def play_audio():
    global output_audio, p, audio_index
    chunk_size = 1024
    width = 2
    channels = 2
    sample_rate = 44100
    curr_audio_index = audio_index

    audio_input = p.open(format=p.get_format_from_width(width),
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk_size,
                    input_device_index=curr_audio_index)

    while running:
        if output_audio:
            data = audio_input.read(chunk_size)  # read audio stream
            audio_input.write(data, chunk_size)  # play back audio stream
            if curr_audio_index != audio_index:
                audio_input.stop_stream()
                audio_input.close()
                curr_audio_index = audio_index
                audio_input = p.open(format=p.get_format_from_width(width),
                                     channels=channels,
                                     rate=sample_rate,
                                     input=True,
                                     output=True,
                                     frames_per_buffer=chunk_size,
                                     input_device_index=curr_audio_index)
        else:
            time.sleep(1)
    audio_input.stop_stream()
    audio_input.close()
    p.terminate()
    print("Audio finished!")


def show_video():
    global frame, stream, window_stream, output_video
    window_is_open = False
    while running:
        if use_window_capture:
            ret, frame = True, window_stream.get_screenshot()
        else:
            ret, frame = stream.read()
        if ret and output_video:
            window_is_open = True
            try:
                cv2.imshow('Video Stream', frame)
            except cv2.error:
                pass  # in some rare cases, switching causes an error
        elif window_is_open:
            cv2.destroyWindow("Video Stream")
            window_is_open = False
        if cv2.waitKey(1) & 0xFF == ord('q'):
            output_video = False
    cv2.destroyAllWindows()
    print("Finished video!")


def mainloop():
    global current_kingdom, frame

    # Set up Eel
    eel.init('gui')  # Initialize the gui package
    eel.start('index.html', port=8083, size=GUI_SIZE, block=False)  # start the GUI
    eel.set_current_kingdom(current_kingdom)

    # Final setup variables
    change_kingdom = ""  # Confirmation variable for kingdom changes
    check_kingdom_at = time.time()  # Check right after start
    check_moon_at = time.time()  # Check right after start
    check_story_at = time.time()  # Check right after start
    old_time = time.time()  # start time for loop
    text_potential = 0  # So we don't read partial text

    ########################################################################################################################
    # Begin main loop, where all of the detection happens
    ########################################################################################################################
    while running:
        new_time = time.time()
        frame_time = new_time - old_time
        old_time = new_time
        eel.sleep(0.001)  # sleep of ~0.001 is the minimum allowed, still works

        if frame is None or frame.size == 0:
            continue
        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Resizing image needed for distortion correction. NEAREST is ~8x faster than default but riskier so still testing
        image = Image.fromarray(image[borders[1]:borders[3], borders[0]:borders[2]]).resize((IM_WIDTH, IM_HEIGHT))

        # Check kingdom every 3s
        if not manually_switch_kingdoms and new_time > check_kingdom_at:
            check_kingdom_at = new_time + KINGDOM_TIMER  # Reset timer
            kingdom_check_im = image_to_bw(image.crop(KINGDOM_BORDERS))  # Must be 50x50 to work in model
            new_kingdom = update_kingdom(kingdom_check_im)
            if new_kingdom and new_kingdom != current_kingdom:  # strong match for new
                if change_kingdom == new_kingdom:  # make sure we get two in a row of the same kingdom
                    current_kingdom = new_kingdom
                    eel.set_current_kingdom(current_kingdom)
                    change_kingdom = ""
                    if VERBOSE:
                        print("Kingdom changed to: ", new_kingdom)
                else:
                    change_kingdom = new_kingdom
                    check_kingdom_at = new_time + 1  # Perform the second check in 1s to be sure
                continue  # if purple coin logo visible, not getting a moon or talking to Talkatoo
            change_kingdom = ""

        # Moon recognition every half second
        if new_time > check_moon_at:
            moon_check_im = image_to_bw(image.crop(language_settings["Moon_Bounds"]), white=230)
            if is_text_naive(moon_check_im, language_settings["Text_Height"], language_settings["Text_Lower"]+0.1, language_settings["Text_Upper"]+0.1, VERBOSE):
                moon_matches = match_moon_text(moon_check_im, prepend="Collected")
                if moon_matches:
                    if not collected_moons or moon_matches != collected_moons[-1]:
                        collected_moons.append(moon_matches)
                        eel.add_collected_moon(moon_matches)
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
                    moon_matches = match_moon_text(story_text, prepend="Collected", story=True)
                    collected_moons.append(moon_matches)
                    eel.add_collected_moon(moon_matches)
                    check_story_at = new_time + 10
                    continue

                multi_check_im = image.crop(MULTI_BORDERS)
                if check_story_multi(multi_check_im, expected="MULTI"):
                    if VERBOSE:
                        print("Got a multi moon!", end=" ")  # Don't bother with OCR since moon border makes it unreliable
                    multi_text = image.rotate(-3.5).crop(STORY_TEXT_BORDERS)
                    multi_text = image_to_bw(multi_text, white=240)
                    moon_matches = match_moon_text(multi_text, prepend="Collected", multi=True)
                    collected_moons.append(moon_matches)
                    eel.add_collected_moon(moon_matches)
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
                    moon_matches = match_moon_text(talkatoo_text, prepend="Unlocked")
                    if moon_matches:  # Found at least one match
                        if not mentioned_moons or moon_matches != mentioned_moons[-1]:  # Allow nonconsecutive duplicates
                            mentioned_moons.append(moon_matches)
                            eel.add_mentioned_moon(moon_matches)
        else:
            text_potential = 0


if __name__ == "__main__":
    ####################################################################################################################
    # Define variables used for computation
    ####################################################################################################################
    this_OS = platform.system()
    moons_by_kingdom, hint_arts = generate_moon_dict()
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
        use_window_capture = settings["useWindowCapture"]
        window_capture_name = settings["windowCaptureName"]
        window_capture_cropping = settings["windowCaptureCropping"]
        if settings["videoDevice"]:
            video_index = get_index_for(settings["videoDevice"]["device_name"])
        else:
            video_index = DEFAULT_VIDEO_INDEX
        if settings["audioDevice"]:
            audio_index = get_index_for(settings["audioDevice"]["index"])
        else:
            audio_index = DEFAULT_AUDIO_INDEX
        is_postgame = settings["includePostGame"]
        include_extra_kingdoms = settings["includeWithoutTalkatoo"]
        output_audio = settings["autoPlayOutputStreams"]
        output_video = settings["autoPlayOutputStreams"]
        manually_switch_kingdoms = settings.get("manuallySwitchKingdoms", False)
    else:
        translate_from = DEFAULT_GAME_LANGUAGE
        translate_to = DEFAULT_GUI_LANGUAGE
        use_window_capture = False
        window_capture_name = None
        window_capture_cropping = [0, 0, 0, 0]
        video_index = DEFAULT_VIDEO_INDEX
        audio_index = DEFAULT_AUDIO_INDEX
        is_postgame = False
        include_extra_kingdoms = False
        output_audio = False
        output_video = False
        manually_switch_kingdoms = False
    language_settings = LANGUAGES[translate_from]
    reader = easyocr.Reader([language_settings["Language"]], verbose=False)
    score_func = score_logogram if translate_from in ["chinese_traditional", "chinese_simplified", "japanese",
                                                      "korean"] else score_alphabet

    # Set up video source
    p = pyaudio.PyAudio()
    stream = cv2.VideoCapture(video_index)  # Set up capture card
    window_stream = None
    set_window_capture(window_capture_name, True)  # Set up window capture
    frame = None
    borders = reset_capture_borders()[0]  # Find borders to crop every iteration

    if VERBOSE:
        print("Setup complete! You may now approach the bird.\n")

    video_stream = threading.Thread(target=show_video)
    audio_stream = threading.Thread(target=play_audio)
    running = True  # Ends everything

    # creating thread
    video_stream.start()
    audio_stream.start()
    mainloop()
