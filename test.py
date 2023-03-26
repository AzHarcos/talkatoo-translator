import cv2
from time import time
from window_capture import *
from platform import system

this_OS = system()

if this_OS == "Windows":
    windows = list_open_windows()
    projector_window = next(window for window in windows if "Projector" in window["name"])

    loop_time = time()
    while True:

        # get an updated image
        window_capture = WindowCapture(projector_window["hwnd"])
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

