""" https://pyimagesearch.com/2015/09/07/blur-detection-with-opencv/ """

import cv2

import globals


class FocusMesure:
    def __init__(self):
        self.window_width = globals.FOCUS_CENTER_WIDTH
        self.window_height = globals.FOCUS_CENTER_HEIGHT
        self.focus_mode = globals.FOCUS_TYPE_CENTER_100X100
        self.last_focus_level = 0

    def set_window_width(self, width):
        self.window_width = width

    def get_window_width(self):
        return self.window_width

    def set_window_height(self, height):
        self.window_width = height

    def get_window_height(self):
        return self.window_height

    def set_focus_mode(self, f_mode):
        if f_mode == globals.FOCUS_TYPE_NONE:
            self.focus_mode = globals.FOCUS_TYPE_NONE
        elif f_mode == globals.FOCUS_TYPE_CENTER_50X50:
            self.focus_mode = globals.FOCUS_TYPE_CENTER_50X50
            self.window_width = 50
            self.window_height = 50
        elif f_mode == globals.FOCUS_TYPE_CENTER_100X100:
            self.focus_mode = globals.FOCUS_TYPE_CENTER_100X100
            self.window_width = 100
            self.window_height = 100
        elif f_mode == globals.FOCUS_TYPE_CENTER_200X200:
            self.focus_mode = globals.FOCUS_TYPE_CENTER_200X200
            self.window_width = 200
            self.window_height = 200

    def get_focus_mode(self):
        return self.focus_mode

    def get_focus_center_window_points(self, image):
        shape = image.shape
        frame_width = shape[1]
        frame_height = shape[0]
        window_width = globals.FOCUS_CENTER_WIDTH
        window_height = globals.FOCUS_CENTER_HEIGHT
        start_x = int((frame_width - self.window_width) / 2)
        end_x = int((frame_width + self.window_width) / 2)
        start_y = int((frame_height - self.window_height) / 2)
        end_y = int((frame_height + self.window_height) / 2)
        return start_x, end_x, start_y, end_y

    def _variance_of_laplacian(self, image):
        # compute the Laplacian of the image and then return the focus
        # measure, which is simply the variance of the Laplacian
        return cv2.Laplacian(image, cv2.CV_64F).var()

    def get_focus_measure_center(self, image, window_width, window_height):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_width, image_height = gray_image.shape
        start_x = int((image_width - window_width) / 2)
        end_x = int((image_width + window_width) / 2)
        start_y = int((image_height - window_height) / 2)
        end_y = int((image_height + window_height) / 2)
        cropped_gray_image = gray_image[start_x:end_x, start_y:end_y]

        self.last_focus_level = self._variance_of_laplacian(cropped_gray_image)
        return self.last_focus_level
