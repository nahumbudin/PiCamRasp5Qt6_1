import os

from PyQt6.QtCore import QPoint
from PyQt6.QtWidgets import QFileDialog, QMessageBox

import WebServerService
import globals
from ImagesDialog import ImagesDialog
from FilesHandling import *

from CustomSignals import PressBackSignal, ImageDisplayUpdateSignal


class MainWindowDisplayControl:
    """ This class manges and controls the selection of the active display V3. """
    # Events
    KEY_PRESSED_PARAMS = 0
    KEY_PRESSED_IMAGES = 1
    KEY_PRESSED_INTERFACES = 2
    KEY_PRESSED_4 = 3
    KEY_PRESSED_BACK = 4
    IMAGE_PIC_CLICKED = 5
    SHOOT_SWITCH_PRESSED = 6
    # Display states
    DISPLAY_STATE_SHOW_PARAMS_DIALOG = 0
    DISPLAY_STATE_SHOW_IMAGES_DIALOG = 1
    DISPLAY_STATE_SHOW_INTERFACES_DIALOG = 2
    DISPLAY_STATE_SHOW_HW_PARAMS_DIALOG = 3
    DISPLAY_STATE_SHOW_IMAGE_VIEW = 4

    def __init__(self, main_window_ui, param_config_setting,
                 sys_events_dic=None, custom_sigs_dic=None,
                 files_handler=None):
        self._app_main_window = main_window_ui
        self._params_configuration_settings = param_config_setting
        self._sys_events_dictionary = sys_events_dic
        self._custom_signals_dictionary = custom_sigs_dic
        self._display_state = self.DISPLAY_STATE_SHOW_PARAMS_DIALOG
        # Pix is the default widget
        self.back_button_clicked()

        self._images_in_selected_directory = []
        self._selected_image_path = ""
        self._selected_image_name = ""
        self._selected_image_index = 0
        self._current_1st_image = 0

        self._selected_image_found = False

        self._images_dialog = None

        self.connected_ip = "0.0.0.0"
        self.connected_ssid = "SSID"

        self.files_handler = files_handler

    def _set_display_mode(self, state=DISPLAY_STATE_SHOW_PARAMS_DIALOG):
        """ This function set the display active elements according to the camera state. """
        self._display_state = state

        if self._display_state == self.DISPLAY_STATE_SHOW_PARAMS_DIALOG:
            self._app_main_window.tab_widget_params.show()
            self._app_main_window.widget_images.hide()
            self._app_main_window.widget_interfaces.hide()
            self._app_main_window.widget_hw.hide()
            self._app_main_window.label_param_lux_display.hide()
            self._app_main_window.label_param_gain_display.hide()
            self._app_main_window.label_param_focus_display.hide()
            self._app_main_window.label_param_exp_time_display.hide()

        elif self._display_state == self.DISPLAY_STATE_SHOW_IMAGES_DIALOG:
            self._app_main_window.tab_widget_params.hide()
            self._app_main_window.widget_images.show()
            self._app_main_window.widget_interfaces.hide()
            self._app_main_window.widget_hw.hide()
            self._app_main_window.label_param_lux_display.hide()
            self._app_main_window.label_param_gain_display.hide()
            self._app_main_window.label_param_focus_display.hide()
            self._app_main_window.label_param_exp_time_display.hide()

        elif self._display_state == self.DISPLAY_STATE_SHOW_INTERFACES_DIALOG:
            self._app_main_window.tab_widget_params.hide()
            self._app_main_window.widget_images.hide()
            self._app_main_window.widget_interfaces.show()
            self._app_main_window.widget_hw.hide()
            self._app_main_window.label_param_lux_display.hide()
            self._app_main_window.label_param_gain_display.hide()
            self._app_main_window.label_param_focus_display.hide()
            self._app_main_window.label_param_exp_time_display.hide()

        elif self._display_state == self.DISPLAY_STATE_SHOW_HW_PARAMS_DIALOG:
            self._app_main_window.tab_widget_params.hide()
            self._app_main_window.widget_images.hide()
            self._app_main_window.widget_interfaces.hide()
            self._app_main_window.widget_hw.show()
            self._app_main_window.label_param_lux_display.hide()
            self._app_main_window.label_param_gain_display.hide()
            self._app_main_window.label_param_focus_display.hide()
            self._app_main_window.label_param_exp_time_display.hide()

        elif self._display_state == self.DISPLAY_STATE_SHOW_IMAGE_VIEW:
            self._app_main_window.tab_widget_params.hide()
            self._app_main_window.widget_images.hide()
            self._app_main_window.widget_interfaces.hide()
            self._app_main_window.widget_hw.hide()
            # self._app_main_window.label_pix.show()

            if self._params_configuration_settings.get_on_screen_parameters_display_enable_state():
                self._app_main_window.label_param_lux_display.show()
                self._app_main_window.label_param_gain_display.show()
                self._app_main_window.label_param_focus_display.show()
                self._app_main_window.label_param_exp_time_display.show()
            else:
                self._app_main_window.label_param_lux_display.hide()
                self._app_main_window.label_param_gain_display.hide()
                self._app_main_window.label_param_focus_display.hide()
                self._app_main_window.label_param_exp_time_display.hide()

            self._app_main_window.pushButton_back.lower()
            self._app_main_window.horizontalSlider_params_active.hide()
            self._app_main_window.label_param_active_name.hide()
            self._app_main_window.lineEdit_parms_active.hide()
            self._app_main_window.pushButton_label_pix.blockSignals(False)
            self._display_state = self.DISPLAY_STATE_SHOW_IMAGE_VIEW

    def _select_image_to_show(self, open_qfile_dialog=True):
        """ this function opens a file selection dialog to select a stored image to show. """
        if open_qfile_dialog:
            selected_file_name = QFileDialog.getOpenFileNames(self._app_main_window.centralwidget,
                                                              'Select File', self.files_handler.get_active_images_dir(),
                                                              'Images (*.jpg)')
            self.files_handler.set_last_selected_image_file(selected_file_name)
        else:
            # Get last selected file name in a data format returned by the QFileDialog
            selected_file_name = ([self.files_handler.get_last_selected_image_file()], 'Images (*jpg)')

        # print(selected_file_name)

        if len(selected_file_name[0]) > 0:

            self._images_in_selected_directory.clear()

            self._selected_image_path = os.path.dirname(selected_file_name[0][0])
            self._selected_image_name = os.path.basename(selected_file_name[0][0])

            # print(self._selected_image_path, self._selected_image_name)

            self.files_handler.set_active_images_dir(self._selected_image_path)

            # Get all the images in the selected directory.
            for image_file in os.listdir(self._selected_image_path):
                self._images_in_selected_directory.append(image_file)

            # Sort the list
            self._images_in_selected_directory.sort()

            # print(self._images_in_selected_directory)

            # find the selected image
            self._selected_image_index = self._images_in_selected_directory.index(self._selected_image_name)
            self._current_1st_image = self._selected_image_index

            # Open the images thumbnails dialog
            self._images_dialog = ImagesDialog(parent=self._app_main_window.centralwidget,
                                               # back_signal=self.press_back_signal,
                                               back_signal=self._custom_signals_dictionary["PressBackSignal"],
                                               update_disp_image_signal=
                                               self._custom_signals_dictionary["ImageDisplayUpdateSignal"],
                                               close_done_signal=
                                               self._custom_signals_dictionary["ImagesDialogCloseDoneSignal"],
                                               select_image_signal=self._custom_signals_dictionary["ImageSelectSignal"],
                                               close_done_event=
                                               self._sys_events_dictionary["close_the_image_dialog_event"],
                                               disp_width=self._app_main_window.centralwidget.width(),
                                               disp_height=self._app_main_window.centralwidget.height(),
                                               files_handler=self.files_handler)

            # Reposition
            point = parent = self._app_main_window.centralwidget.rect().topLeft()
            # Set this point as a global position
            global_point = self._app_main_window.centralwidget.mapToGlobal(point)
            # By default, a widget will be placed from its top-left corner, so
            # we need to move it up by 30 pixels - the window title height
            self._images_dialog.move(global_point - QPoint(0, 30))

            self._images_dialog.update_display(self._images_in_selected_directory,
                                               self._current_1st_image,
                                               self._selected_image_path)

            self._images_dialog.exec()

        else:
            # No image was selected.
            self.back_button_clicked()

    def params_button_clicked(self):
        if not self._display_state == self.DISPLAY_STATE_SHOW_PARAMS_DIALOG:
            self._set_display_mode(self.DISPLAY_STATE_SHOW_PARAMS_DIALOG)
            self._sys_events_dictionary["params_clicked_event"].set()
            self._sys_events_dictionary["user_activity_event"].set()

    def images_button_clicked(self):
        if True:  # not self._display_state == self.DISPLAY_STATE_SHOW_IMAGES_DIALOG:
            self._set_display_mode(self.DISPLAY_STATE_SHOW_IMAGES_DIALOG)
            self._sys_events_dictionary["images_clicked_event"].set()
            self._sys_events_dictionary["user_activity_event"].set()
            self._select_image_to_show(open_qfile_dialog=True)

    def reopen_images_show(self):
        self._set_display_mode(self.DISPLAY_STATE_SHOW_IMAGES_DIALOG)
        self._sys_events_dictionary["images_clicked_event"].set()
        self._sys_events_dictionary["user_activity_event"].set()
        self._select_image_to_show(open_qfile_dialog=False)

    def interfaces_button_clicked(self):
        if not self._display_state == self.DISPLAY_STATE_SHOW_INTERFACES_DIALOG:
            self._set_display_mode(self.DISPLAY_STATE_SHOW_INTERFACES_DIALOG)
            self._sys_events_dictionary["interfaces_clicked_event"].set()
            self._sys_events_dictionary["user_activity_event"].set()
            self.update_interfaces_info()

    def hardware_button_clicked(self):
        if not self._display_state == self.DISPLAY_STATE_SHOW_HW_PARAMS_DIALOG:
            self._set_display_mode(self.DISPLAY_STATE_SHOW_HW_PARAMS_DIALOG)
            self._sys_events_dictionary["hw_clicked_event"].set()
            self._sys_events_dictionary["user_activity_event"].set()

    def back_button_clicked(self):
        if not self._display_state == self.DISPLAY_STATE_SHOW_IMAGE_VIEW:
            self._set_display_mode(self.DISPLAY_STATE_SHOW_IMAGE_VIEW)
            self._sys_events_dictionary["back_clicked_event"].set()

        elif self._display_state == self.DISPLAY_STATE_SHOW_IMAGES_DIALOG:
            self._sys_events_dictionary["close_the_image_dialog_event"].set()

        self._sys_events_dictionary["user_activity_event"].set()
        self._sys_events_dictionary["exit_power_save_state_event"].set()

    def pix_clicked(self):  # This must be changed - move flow to state machine
        # print("Pix Clicked")
        self._sys_events_dictionary["display_clicked_event"].set()
        self._sys_events_dictionary["user_activity_event"].set()

    def shoot_switch_pressed(self):
        # print("Main win control - shoot")
        self._sys_events_dictionary["user_activity_event"].set()

    def exit_clicked(self):
        exit_reply = QMessageBox.question(self._app_main_window.centralwidget,
                                          'Exit Camera Application', "Are you sure you want to exit?",
                                          (QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No),
                                          QMessageBox.StandardButton.No)
        if exit_reply == QMessageBox.StandardButton.Yes:
            self._sys_events_dictionary["camera_process_exit_event"].set()
            self._sys_events_dictionary["update_display_thread_exit_event"].set()
            exit(0)

    def set_qt_ui_connections(self):
        """ Create the connections between the display objects and the signals. """
        self._app_main_window.pushButton_settings_params.clicked.connect(self.params_button_clicked)
        self._app_main_window.pushButton_settings_images.clicked.connect(self.images_button_clicked)
        self._app_main_window.pushButton_settings_interfaces.clicked.connect(self.interfaces_button_clicked)
        self._app_main_window.pushButton_settings_hw.clicked.connect(self.hardware_button_clicked)
        self._app_main_window.pushButton_back.clicked.connect(self.back_button_clicked)
        self._app_main_window.pushButton_label_pix.clicked.connect(self.pix_clicked)
        self._app_main_window.pushButton_exit.clicked.connect(self.exit_clicked)

    def update_interfaces_info(self):
        self.connected_ip = WebServerService.get_host_wlan_ip()
        self.connected_ssid = WebServerService.get_wifi_ssd()

        self._app_main_window.textEdit_wifi_net.setText(self.connected_ssid)
        self._app_main_window.textEdit_wifi_ip.setText(self.connected_ip)
