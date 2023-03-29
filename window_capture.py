import ctypes
import numpy as np
from PIL import ImageGrab
import win32gui, win32ui, win32con # pip install pywin32
from pywintypes import error
from util_functions import *

user32 = ctypes.windll.user32


def list_open_windows():
    open_windows = []

    def winEnumHandler(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            open_windows.append({"hwnd": hwnd, "name": win32gui.GetWindowText(hwnd)})

    win32gui.EnumWindows(winEnumHandler, None)
    return open_windows


class WindowCapture:
    # properties
    width = 0
    height = 0
    hwnd = None
    crop_left = 0
    crop_top = 0
    crop_right = 0
    crop_bottom = 0

    # constructor
    def __init__(self, hwnd, crop_values=None):
        if hwnd is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = hwnd

        self.width, self.height = ImageGrab.grab().size
        self.width -= 1
        self.height -= 1

        window_img = np.array(self.get_screenshot(cropped=False))
        self.borders = determine_borders(window_img)
        self.iheight = self.borders[3] - self.borders[1]
        self.iwidth = self.borders[2] - self.borders[0]
        # get the crop values
        if crop_values is not None:
            self.crop_left, self.crop_top, self.crop_right, self.crop_bottom = crop_values

    def get_screenshot(self, cropped=True):
        try:
            # get the window image data
            window_dc = win32gui.GetWindowDC(self.hwnd)
            dc_object = win32ui.CreateDCFromHandle(window_dc)
            compatible_dc = dc_object.CreateCompatibleDC()
            data_bitmap = win32ui.CreateBitmap()
            data_bitmap.CreateCompatibleBitmap(dc_object, self.width, self.height)
            compatible_dc.SelectObject(data_bitmap)
            compatible_dc.BitBlt((0, 0), (self.width, self.height), dc_object, (0, 0), win32con.SRCCOPY)

            # allow recording hardware accelerated windows
            print_window_flag = 0x00000002
            user32.PrintWindow(self.hwnd, dc_object.GetSafeHdc(), print_window_flag)

            # convert the raw data into a format opencv can read
            img = np.fromstring(data_bitmap.GetBitmapBits(True), dtype='uint8')
            img.shape = (self.height, self.width, 4)

            # free resources
            dc_object.DeleteDC()
            compatible_dc.DeleteDC()
            win32gui.ReleaseDC(self.hwnd, window_dc)
            win32gui.DeleteObject(data_bitmap.GetHandle())

            # drop the alpha channel, or cv.matchTemplate() will throw an error like:
            #   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type()
            #   && _img.dims() <= 2 in function 'cv::matchTemplate'
            img = img[...,:3]

            # make image C_CONTIGUOUS to avoid errors that look like:
            #   File ... in draw_rectangles
            #   TypeError: an integer is required (got type tuple)
            # see the discussion here:
            # https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
            img = np.ascontiguousarray(img)

            # crop image if needed
            if cropped:
                img = img[self.borders[1]+self.crop_top: self.borders[3]-self.crop_bottom,
                          self.borders[0]+self.crop_left:self.borders[2]-self.crop_right]
            return img

        except (win32ui.error, error):
            print("[STATUS] -> Could not read window capture image")
            return None
