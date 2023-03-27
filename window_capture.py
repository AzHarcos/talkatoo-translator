import ctypes
import numpy as np
from PIL import ImageGrab
import win32gui, win32ui, win32con # pip install pywin32

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
    cropped_x = 0
    cropped_y = 0
    offset_x = 0
    offset_y = 0

    # constructor
    def __init__(self, hwnd):
        if hwnd is None:
            self.hwnd = win32gui.GetDesktopWindow()
        else:
            self.hwnd = hwnd

        # get the window size
        self.width, self.height = ImageGrab.grab().size  # screen size
        self.cropped_x = 3
        self.cropped_y = 3
        self.width -= 4
        self.height -= 1
        self.offset_x = 0
        self.offset_y = 0

    def get_screenshot(self):
        try:
            # get the window image data
            window_dc = win32gui.GetWindowDC(self.hwnd)
            dc_object = win32ui.CreateDCFromHandle(window_dc)
            compatible_dc = dc_object.CreateCompatibleDC()
            data_bitmap = win32ui.CreateBitmap()
            data_bitmap.CreateCompatibleBitmap(dc_object, self.width, self.height)
            compatible_dc.SelectObject(data_bitmap)
            compatible_dc.BitBlt((0, 0), (self.width, self.height), dc_object, (self.cropped_x, self.cropped_y), win32con.SRCCOPY)

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

            return img
        except win32ui.error:
            print("[STATUS] -> Could not read window capture image")
            return None
