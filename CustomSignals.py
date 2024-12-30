import numpy as np
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6 import QtGui


class InfoDisplayUpdateSignal(QObject):
    info_custom_signal = pyqtSignal(str)

    def connect_to_slot(self, slot):
        self.info_custom_signal.connect(slot)

    def emit_signal(self, message_string):
        self.info_custom_signal.emit(message_string)


class ImageDisplayUpdateSignal(QObject):
    pix_custom_signal = pyqtSignal(QtGui.QPixmap)

    def connect_to_slot(self, slot):
        self.pix_custom_signal.connect(slot)

    def emit_signal(self, pix_image):
        self.pix_custom_signal.emit(pix_image)


class NumpyArrayImageHistogramPlotSignal(QObject):
    img_hist_custom_signal = pyqtSignal(np.ndarray)

    def connect_to_slot(self, slot):
        self.img_hist_custom_signal.connect(slot)

    def emit_signal(self, array_image):
        self.img_hist_custom_signal.emit(array_image)


class PressBackSignal(QObject):
    back_custom_signal = pyqtSignal()

    def connect_to_slot(self, slot):
        self.back_custom_signal.connect(slot)

    def emit_signal(self):
        self.back_custom_signal.emit()


class ReopenImagesSignal(QObject):
    reopen_images_custom_signal = pyqtSignal()

    def connect_to_slot(self, slot):
        self.reopen_images_custom_signal.connect(slot)

    def emit_signal(self):
        self.reopen_images_custom_signal.emit()


class PressParamsSignal(QObject):
    params_custom_signal = pyqtSignal()

    def connect_to_slot(self, slot):
        self.params_custom_signal.connect(slot)

    def emit_signal(self):
        self.params_custom_signal.emit()


class SelectImageSignal(QObject):
    select_image_custom_signal = pyqtSignal()

    def connect_to_slot(self, slot):
        self.select_image_custom_signal.connect(slot)

    def emit_signal(self):
        self.select_image_custom_signal.emit()


class PressInterfacesSignal(QObject):
    interfaces_custom_signal = pyqtSignal()

    def connect_to_slot(self, slot):
        self.interfaces_custom_signal.connect(slot)

    def emit_signal(self):
        self.interfaces_custom_signal.emit()


class ShowHideImageViewSignal(QObject):
    show_hide_image_view_custom_signal = pyqtSignal(bool)

    def connect_to_slot(self, slot):
        self.show_hide_image_view_custom_signal.connect(slot)

    def emit_signal(self, show):
        self.show_hide_image_view_custom_signal.emit(show)


class ImagesDialogCloseSignal(QObject):
    images_dialog_close_custom_signal = pyqtSignal()

    def connect_to_slot(self, slot):
        self.images_dialog_close_custom_signal.connect(slot)

    def emit_signal(self):
        self.images_dialog_close_custom_signal.emit()


class CloseTheImagesDialogSignal(QObject):
    close_the_images_dialog_custom_signal = pyqtSignal()

    def connect_to_slot(self, slot):
        self.close_the_images_dialog_custom_signal.connect(slot)

    def emit_signal(self):
        self.close_the_images_dialog_custom_signal.emit()
