import cv2
from time import time
from window_capture import WindowCapture
import pyautogui # pip install pyautogui

obs_window_title = next(title for title in pyautogui.getAllTitles() if "OBS" in title)
print(obs_window_title)
window_capture = WindowCapture(obs_window_title)
print(window_capture)

loop_time = time()
while True:

    # get an updated image
    screenshot = window_capture.get_screenshot()

    cv2.imshow('Computer Vision', screenshot)

    # debug the loop rate
    print('FPS {}'.format(1 / (time() - loop_time)))
    loop_time = time()

    # press 'q' with the output window focused to exit.
    # waits 1 ms every loop to process key presses
    if cv2.waitKey(1) == ord('q'):
        cv2.destroyAllWindows()
        break

