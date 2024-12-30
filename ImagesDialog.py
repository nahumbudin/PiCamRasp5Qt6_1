import threading
import time

from PyQt6.QtWidgets import QDialog
from PIL import Image
from numpy import asarray
from matplotlib import pyplot as plt

import globals
from ConvertScaleFrame import convert_and_scale_frame
from GetScaleStoredImage import get_scale_stored_image
from HistogramPlot import plot_image_histogram
from Images_Dialog import Ui_Dialog_images

from FilesHandling import *

num_of_images_to_display = 8


class ImagesDialog(QDialog, Ui_Dialog_images):
    def __init__(self, parent=None,
                 back_signal=None,
                 update_disp_image_signal=None,
                 close_done_signal=None,
                 select_image_signal=None,
                 close_done_event=None,
                 disp_width=800, disp_height=600,
                 files_handler=None,
                 **kwargs):
        super(QDialog, self).__init__(parent)
        self.ui = Ui_Dialog_images()
        self.ui.setupUi(self)
        self.first_update_done = False
        self.first_image_index = 0
        self.directory_images = []
        self.images_path = ""
        self.back_signal = back_signal
        self.update_display_image_signal = update_disp_image_signal
        self.select_image_signal = select_image_signal
        self.close_done_signal = close_done_signal
        self.display_width = disp_width
        self.display_height = disp_height

        self.files_handler = files_handler

        self.close_done_event = close_done_event
        self.thread_is_running = True

        self.thumbnail_width = self.ui.label_image_1.width()
        self.thumbnail_height = self.ui.label_image_1.height()

        self.thumbnails_list = [self.ui.label_image_1, self.ui.label_image_2,
                                self.ui.label_image_3, self.ui.label_image_4,
                                self.ui.label_image_5, self.ui.label_image_6,
                                self.ui.label_image_7, self.ui.label_image_8]

        self.thumbnails_names_list = [self.ui.label_image_name_1, self.ui.label_image_name_2,
                                      self.ui.label_image_name_3, self.ui.label_image_name_4,
                                      self.ui.label_image_name_5, self.ui.label_image_name_6,
                                      self.ui.label_image_name_7, self.ui.label_image_name_8]

        self.image_pushbuttons_list = [self.ui.pushButton_image_1, self.ui.pushButton_image_2,
                                       self.ui.pushButton_image_3, self.ui.pushButton_image_4,
                                       self.ui.pushButton_image_5, self.ui.pushButton_image_6,
                                       self.ui.pushButton_image_7, self.ui.pushButton_image_8]

        self.ui.pushButton_imagest_exit.clicked.connect(self.on_done_clicked)
        self.ui.pushButton_images_next.clicked.connect(self.on_next_clicked)
        self.ui.pushButton_images_previous.clicked.connect(self.on_previous_clicked)

        self.ui.pushButton_image_1.clicked.connect(self.on_image_click_1)
        self.ui.pushButton_image_2.clicked.connect(self.on_image_click_2)
        self.ui.pushButton_image_3.clicked.connect(self.on_image_click_3)
        self.ui.pushButton_image_4.clicked.connect(self.on_image_click_4)
        self.ui.pushButton_image_5.clicked.connect(self.on_image_click_5)
        self.ui.pushButton_image_6.clicked.connect(self.on_image_click_6)
        self.ui.pushButton_image_7.clicked.connect(self.on_image_click_7)
        self.ui.pushButton_image_8.clicked.connect(self.on_image_click_8)

        self.wait_thread = threading.Thread(target=self.wait_for_close_event_thread, daemon=True,
                                            args=(self.close_done_event, 1))

        self.actual_num_of_images_to_display = 0

        self.wait_thread.start()

    def wait_for_close_event_thread(self, close_event, dummy_arg):
        print("Image Dialog Wait Thread is Running")
        self.close_done_event = close_event
        self.thread_is_running = True

        while self.thread_is_running:
            if self.close_done_event.is_set():
                self.close_done_event.clear()
                self.thread_is_running = False

                self.on_done_clicked()

            time.sleep(0.05)

    def closeEvent(self, event):
        self.close()
        self.close_done_signal.emit_signal()

    def on_done_clicked(self):
        self.close()
        self.close_done_signal.emit_signal()

    def on_previous_clicked(self):
        if self.first_update_done:
            self.first_image_index -= num_of_images_to_display
            if self.first_image_index < 0:
                self.first_image_index = 0

            self._update_display()

    def on_next_clicked(self):
        if self.first_update_done:
            if self.first_image_index < num_of_images_to_display:
                self.first_image_index = 0
            else:
                self.first_image_index += num_of_images_to_display
                if self.first_image_index > len(self.directory_images) - num_of_images_to_display:
                    self.first_image_index = len(self.directory_images) - num_of_images_to_display

            self._update_display()

    def update_display(self, directory_images, first_image_index, images_path):
        self.directory_images = directory_images
        self.first_image_index = first_image_index
        self.images_path = images_path

        if len(self.directory_images) < 0:
            return

        if self.back_signal is None:
            return

        if self.first_image_index > len(self.directory_images) - num_of_images_to_display:
            self.first_image_index = len(self.directory_images) - num_of_images_to_display

        if self.first_image_index < 0:
            self.first_image_index = 0

        if self.images_path == "":
            self.images_path = globals.DEFAULT_IMAGES_DIR

        for index in range(0, num_of_images_to_display):
            self.image_pushbuttons_list[index].setFlat(False)

        self.first_update_done = True
        self._update_display()

    def _update_display(self):
        if self.first_update_done:
            self.actual_num_of_images_to_display = min(num_of_images_to_display, len(self.directory_images))
            self.ui.lineEdit_images_path.setText(self.images_path)
            for index in range(0, self.actual_num_of_images_to_display):
                image_index = index + self.first_image_index
                thumbnail, scale = self.get_scaled_image(self.directory_images[image_index], self.images_path)
                self.thumbnails_list[index].setPixmap(thumbnail)
                self.thumbnails_names_list[index].setText(self.directory_images[image_index].removesuffix(".jpg"))
                self.image_pushbuttons_list[index].setFlat(True)

    def get_scaled_image(self, image_name, image_path):
        image_full_name = image_path + '/' + image_name
        captured_image_file = Image.open(image_full_name)
        image_array = asarray(captured_image_file)
        # Convert rgb to bgr
        image_array = image_array[..., ::-1].copy()
        pix, scale = convert_and_scale_frame(image_array, self.thumbnail_width, self.thumbnail_height)
        return pix, scale

    def on_image_click_1(self):
        self._image_clicked(0)

    def on_image_click_2(self):
        self._image_clicked(1)

    def on_image_click_3(self):
        self._image_clicked(2)

    def on_image_click_4(self):
        self._image_clicked(3)

    def on_image_click_5(self):
        self._image_clicked(4)

    def on_image_click_6(self):
        self._image_clicked(5)

    def on_image_click_7(self):
        self._image_clicked(6)

    def on_image_click_8(self):
        self._image_clicked(7)

    def _image_clicked(self, i):
        # set_last_browsed_file_index(i)

        if i not in range(0, self.actual_num_of_images_to_display):
            return

        clicked_image_name = self.directory_images[i + self.first_image_index]
        clicked_image_path = self.images_path + "/" + clicked_image_name
        self.files_handler.set_last_selected_image_file(clicked_image_path)
        # print("Clicked image path", clicked_image_path)

        # plot_image_histogram(clicked_image_path)

        padded_image = get_scale_stored_image(clicked_image_path)

        # Convert frame to QPixmap
        pix, scale = convert_and_scale_frame(padded_image, self.display_width, self.display_height)
        self.update_display_image_signal.emit_signal(pix)

        self.select_image_signal.emit_signal()

        self.close()
