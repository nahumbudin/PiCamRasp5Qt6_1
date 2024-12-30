import time
import threading
from multiprocessing import Process, Queue, Event

import numpy as np
from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QMainWindow

import CameraStates as cmst
from CameraStates import CameraStateMachine
from ConfigurationManager import ConfigurationManager
from ConfigurationLoader import ConfigurationLoader
from FilesHandling import FilesHandling
from HistogramPlot import plot_image_histogram
from Main_Window import Ui_MainWindow
import CustomSignals
from CustomSignals import *
from ParametersConfigurationSettingsGuiManager import ParametersConfigurationSettingsGuiManager
import globals
from MainWindowDisplayControl import MainWindowDisplayControl
from PowerSaveTimerThread import disable_timer_expiration_event, power_save_timer_thread
from update_display import update_display_thread
from CameraGrabProcess import camera_grab_process
from WebServerService import web_server_service
from FocusEstimator import FocusMesure


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, **kwargs):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # This object provides a focus estimation level
        self.focus_measure = FocusMesure()
        self.focus_measure.set_focus_mode(globals.FOCUS_TYPE_CENTER_100X100)

        # This object is used for files handling
        self.files_handler = FilesHandling()

        # Define messages Queues
        # A queue that transfers images from the camera process to the display update thread
        self.video_queue = Queue(maxsize=90)
        # A queue that transfers information data from the camera process to the display update thread
        # (battery parameters, camera on time)
        self.info_queue = Queue(maxsize=15)
        # A queue that transfers file management parameters to the camera process
        self.file_management_queue = Queue(maxsize=50)
        # A queue that transfers configuration commands to the camera process
        self.cam_config_queue = Queue(maxsize=50)

        # Define system Events
        # When set, this event makes the camera process to exit.
        self.camera_process_exit_event = Event()
        # When set, this event makes the display update thread to exit.
        self.update_display_thread_exit_event = Event()
        # When set, this event pause the frame grabbing
        self.pause_grabbing_event = Event()
        # When set, this event resumes the frame grabbing
        self.resume_grabbing_event = Event()
        # This event is set when the shoot switch is pressed
        self.shoot_event = Event()
        # This event is set when the shoot switch is released
        self.released_event = Event()
        # This event is set to initiate a frame grabbing
        self.grab_frame_event = Event()
        # This event is set when the main display image is clicked
        self.display_clicked_event = Event()
        # This event is set when the "Back" pushbutton is clicked
        self.back_click_event = Event()
        # This event is set when the "Images" pushbutton is clicked
        self.images_clicked_event = Event()
        # This event is set when an image is selected
        self.image_selected_event = Event()
        # This event is set when the Images dialog "Done" pushbutton is clicked
        self.images_dialog_done_close_event = Event()
        # This event is set when the "HW" pushbutton is clicked
        self.hw_clicked_event = Event()
        # This event is set when the "Interfaces" pushbutton is clicked
        self.interfaces_clicked_event = Event()
        # This event is set when the "Settings" pushbutton is pressed
        self.params_clicked_event = Event()
        # This event is used to enable the active parameter setting view.
        self.enable_live_param_setting_view_event = Event()
        # This event is used to disable the active parameter setting view.
        self.disable_live_param_setting_view_event = Event()
        # This event is used to close the Images Dialog
        self.close_the_images_event = Event()
        # This event is used to indicate that user interacts with the camera
        self.user_activity_event = Event()
        # This event is used to signal that the no activity timer expired
        self.no_activity_timer_expired_event = Event()
        # This event is used to terminate the power save timer thread.
        self.exit_power_save_timer_thread_event = Event()
        # This event is set to exit from power save state
        self.exit_power_save_state_event = Event()

        # Custom Qt Signals
        # This signal is used fot updating the info display
        self.update_info_display_signal = InfoDisplayUpdateSignal()
        self.update_info_display_signal.connect_to_slot(self.update_info_display_slot)
        # This signal is used for updating the main image display
        self.update_image_display_signal = ImageDisplayUpdateSignal()
        self.update_image_display_signal.connect_to_slot(self.update_image_display_slot)
        # This signal is used to indicate that the "Back" pushbutton was pressed
        self.press_back_signal = PressBackSignal()
        self.press_back_signal.connect_to_slot(self.back_clicked_slot)
        # This signal is used to indicate that the "Interfaces" pushbutton was pressed
        self.press_interfaces_signal = PressInterfacesSignal()
        self.press_interfaces_signal.connect_to_slot(self.interfaces_clicked_slot)
        # This signal is used to indicate that the "Images" pushbutton was pressed
        self.reopen_images_signal = ReopenImagesSignal()
        self.reopen_images_signal.connect_to_slot(self.reopen_images_slot)
        # This signal is used to indicate that the "Params" pushbutton was pressed
        self.press_params_signal = PressParamsSignal()
        self.press_params_signal.connect_to_slot(self.params_clicked_slot)
        # This signal is used to indicate that one of the displayed stored images was clicked
        self.select_image_signal = SelectImageSignal()
        self.select_image_signal.connect_to_slot(self.select_image_slot)
        # This signal is used to show or hide the image view (label_pix)
        self.show_hide_image_view_signal = ShowHideImageViewSignal()
        self.show_hide_image_view_signal.connect_to_slot(self.show_hide_image_view_slot)
        # this signal is used to indicate that the Images Dialog was closed or the Done key was pressed
        self.images_dialog_close_signal = ImagesDialogCloseSignal()
        self.images_dialog_close_signal.connect_to_slot(self.images_dialog_close_slot)
        # this signal is used to close the Images Dialog
        self.close_the_images_dialog_signal = CloseTheImagesDialogSignal()
        self.close_the_images_dialog_signal.connect_to_slot(self.close_the_images_dialog_slot)
        # This signal is used to plot an histogram of a captured image (array)
        self.numpy_array_image_histogram_plot_signal = NumpyArrayImageHistogramPlotSignal()
        self.numpy_array_image_histogram_plot_signal.connect_to_slot(self.numpy_array_image_histogram_plot_slot)

        # A dictionary of all the os sys Events.
        self.sys_events = {
            "camera_process_exit_event": self.camera_process_exit_event,
            "update_display_thread_exit_event": self.update_display_thread_exit_event,
            "pause_grabbing_event": self.pause_grabbing_event,
            "resume_grabbing_event": self.resume_grabbing_event,
            "shoot_event": self.shoot_event,
            "released_event": self.released_event,
            "grab_frame_event": self.grab_frame_event,
            "display_clicked_event": self.display_clicked_event,
            "back_clicked_event": self.back_click_event,
            "images_clicked_event": self.images_clicked_event,
            "image_selected_event": self.image_selected_event,
            "images_done_close_clicked_event": self.images_dialog_done_close_event,
            "hw_clicked_event": self.hw_clicked_event,
            "interfaces_clicked_event": self.interfaces_clicked_event,
            "params_clicked_event": self.params_clicked_event,
            "enable_live_param_setting_view_event": self.enable_live_param_setting_view_event,
            "disable_live_param_setting_view_event": self.disable_live_param_setting_view_event,
            "close_the_image_dialog_event": self.close_the_images_event,
            "user_activity_event": self.user_activity_event,
            "no_activity_timer_expired_event": self.no_activity_timer_expired_event,
            "exit_power_save_state_event": self.exit_power_save_state_event
        }

        # A dictionary of all the custom signals
        self.custom_signals = {
            "InfoDisplayUpdateSignal": self.update_info_display_signal,
            "ImageDisplayUpdateSignal": self.update_image_display_signal,
            "PressBackSignal": self.press_back_signal,
            "PressParamsSignal": self.press_params_signal,
            "PressInterfacesSignal": self.press_interfaces_signal,
            "ReopenImagesSignal": self.reopen_images_signal,
            "ImageSelectSignal": self.select_image_signal,
            "ShowHideImageViewSignal": self.show_hide_image_view_signal,
            "ImagesDialogCloseDoneSignal": self.images_dialog_close_signal,
            "NumpyArrayImageHistogramPlotSignal": self.numpy_array_image_histogram_plot_signal
        }

        # Thread is running as long as True
        self.wait_for_shoot_switch_pressed_thread_running = False

        # This object is used for handling the camera configuration files and settings
        self.configuration_manager = ConfigurationManager(file_name=globals.DEFAULT_CONFIGURATION_FILE)

        # This object manages the parameters setting GUI
        self.parameters_configuration_settings = (
            ParametersConfigurationSettingsGuiManager(self.ui,
                                                      self.cam_config_queue,
                                                      self.resume_grabbing_event,
                                                      self.enable_live_param_setting_view_event,
                                                      self.user_activity_event,
                                                      self.focus_measure,
                                                      self.configuration_manager))
        self.parameters_configuration_settings.init_configuration_params_display()

        # This object is used to load configuration and set the camera parameters
        self.configuration_loader = ConfigurationLoader(self.configuration_manager,
                                                        self.parameters_configuration_settings)

        # This object manges and controls the selection of the active display.
        self.main_window_display_control = MainWindowDisplayControl(self.ui,
                                                                    self.parameters_configuration_settings,
                                                                    self.sys_events, self.custom_signals,
                                                                    self.files_handler)

        self.main_window_display_control.set_qt_ui_connections()

        self.ui.label_pix.setOpenExternalLinks(True)

        # This object is the camera main state machine withe initial state of show preview
        self.csm = CameraStateMachine(init_state=cmst.STATE_SHOW_PREVIEW,
                                      sys_events_dic=self.sys_events,
                                      custom_sigs_dic=self.custom_signals,
                                      images_q=self.video_queue,
                                      configuration=self.configuration_manager)

        # This thread updates the display
        self.update_thread = threading.Thread(target=update_display_thread, daemon=True,
                                              args=(self.video_queue, self.info_queue,
                                                    self.update_display_thread_exit_event,
                                                    self.update_info_display_signal,
                                                    self.update_image_display_signal,
                                                    self.ui.label_pix,
                                                    self.numpy_array_image_histogram_plot_signal,
                                                    self.focus_measure))

        self.update_thread.start()

        # This thread runs a timer that expires if no user activity is detected. Initial time is set to 1min
        initial_time = 60
        self.camera_power_save_timer_thread = threading.Thread(target=power_save_timer_thread, daemon=True,
                                                               args=(initial_time, self.user_activity_event,
                                                                     self.no_activity_timer_expired_event,
                                                                     self.exit_power_save_timer_thread_event))
        self.camera_power_save_timer_thread.start()

        # This process handles frames grabbing from the camera
        self.grab_process = Process(target=camera_grab_process,
                                    args=(self.video_queue, self.info_queue, self.file_management_queue,
                                          self.cam_config_queue,
                                          self.shoot_event, self.released_event,
                                          self.grab_frame_event, self.camera_process_exit_event,
                                          self.pause_grabbing_event, self.resume_grabbing_event,
                                          800, 480, 30))
        self.grab_process.start()
        self.grab_process.join(0.1)

        # TEMP
        self.file_management_queue.put(globals.DEFAULT_IMAGES_DIR_MSSG)
        self.file_management_queue.put(globals.DEFAULT_IMAGE_FILE_NAME_MSSG)
        self.file_management_queue.put(globals.DEFAULT_IMAGE_FILE_EXTENSION_MSSG)

        self.shoot_switch_wait_thread = threading.Thread(target=self.wait_for_shoot_switch_press_thread, daemon=True)
        self.shoot_switch_wait_thread.start()

        self.ui.widget_histogram.hide()

        # upload and set configuration parameters
        self.configuration_loader.load_and_set_configuration()

    def wait_for_shoot_switch_press_thread(self):
        """ This thread waits for a shoot switch pressed event generated by the IO thread.
            Used for signaling the display control.!!!! """
        self.wait_for_shoot_switch_pressed_thread_running = True

        while self.wait_for_shoot_switch_pressed_thread_running:
            if self.shoot_event.is_set():
                pass
                #print("Main Wait for Shoot Thread")
                # self.shoot_event.clear()
                self.main_window_display_control.shoot_switch_pressed()

            if self.update_display_thread_exit_event.is_set():
                self.wait_for_shoot_switch_pressed_thread_running = False

            time.sleep(0.05)

    def terminate_app(self):
        print("Exiting.....")
        self.camera_process_exit_event.set()
        self.update_display_thread_exit_event.set()
        self.exit_power_save_timer_thread_event.set()
        # self.p.terminate()  <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

    def on_back_pushbutton_pressed(self):
        """ Called when the Back pushbutton is pressed. """
        self.parameters_configuration_settings.on_back_push_button_pressed()
        self.main_window_display_control.back_button_clicked()

    # Qt custom defined Slots
    @pyqtSlot(str)
    def update_info_display_slot(self, message=""):
        """ Parses the information message and update the info display . """
        if len(message) > 0:
            if message[:5] == globals.DEFAULT_CHARGING_STATUS[:5]:
                if message[5] == '1':
                    self.ui.label_hw_charging_on.setText("Charging ON")
                if message[5] == '0':
                    self.ui.label_hw_charging_on.setText("Charging OFF")

            if message[:5] == globals.DEFAULT_BAT_CAPACITY[:5]:
                bat_capacity_str = message[5:]
                self.ui.label_hw_bat_cap.setText((str(f"Battery Capacity:  {bat_capacity_str}%")))
                return

            if message[:5] == globals.DEFAULT_BAT_VOLTAGE[:5]:
                bat_voltage_str = message[5:]
                self.ui.label_hw_bat_vlt.setText((str(f"Battery Voltage:    {bat_voltage_str}V")))
                return

            if message[:5] == globals.DEFAULT_CAMERA_ON_TIME[:5]:
                on_time_str = message[5:]
                self.ui.label_hw_bat_time_on.setText((str(f"Camera On Time:   {on_time_str}")))
                return

            if message[:5] == globals.DEFAULT_CPU_TEMP[:5]:
                cpu_temp_str = message[5:]
                self.ui.label_hw_cpu_temp.setText((str(f"CPU Temperature: {cpu_temp_str} C")))
                return

            if message[:5] == globals.DEFAULT_CPU_USAGE[:5]:
                cpu_usage_str = message[5:]
                self.ui.label_hw_cpu_usage.setText((str(f"CPU Usage:            {cpu_usage_str}%")))
                return

            if message[:5] == globals.DEFAULT_CAMERA_GAIN[:5]:
                camera_gain_str = "Gain " + message[5:]
                self.ui.label_param_gain_display.setText(camera_gain_str)
                return

            if message[:5] == globals.DEFAULT_CAMERA_FOCUS[:5]:
                camera_focus_str = "Focus " + message[5:]
                self.ui.label_param_focus_display.setText(camera_focus_str)
                return

            if message[:5] == globals.DEFAULT_CAMERA_EXP_TIME[:5]:
                expos_time_str = ""
                exposure_time = int(message[5:])
                if exposure_time < 1000:
                    expos_time_str = "Exposure Time " + message[5:] + "us"
                elif exposure_time < 10000:
                    expos_time_str = "Exposure Time " + message[5:6] + "." + message[6:7] + "ms"
                elif exposure_time < 100000:
                    expos_time_str = "Exposure Time " + message[5:7] + "ms"
                elif exposure_time < 1000000:
                    expos_time_str = "Exposure Time " + message[5:8] + "ms"
                elif exposure_time < 10000000:
                    expos_time_str = "Exposure Time " + message[5:6] + "." + message[6:7] + "sec"
                else:
                    expos_time_str = "Exposure Time " + message[5:7] + "sec"

                self.ui.label_param_exp_time_display.setText(expos_time_str)
                return

            if message[:5] == globals.DEFAULT_CAMERA_LUX[:5]:
                camera_lux_str = message[5:] + " Lux"
                self.ui.label_param_lux_display.setText(camera_lux_str)
                return

    @pyqtSlot(QtGui.QPixmap)
    def update_image_display_slot(self, pix_pic=""):
        self.ui.label_pix.setPixmap(pix_pic)
        # print("Update Show Pix")
        # self.ui.label_pix.show()

    @pyqtSlot()
    def back_clicked_slot(self):
        self.on_back_pushbutton_pressed()

    @pyqtSlot()
    def reopen_images_slot(self):
        self.main_window_display_control.reopen_images_show()

    @pyqtSlot()
    def interfaces_clicked_slot(self):
        pass

    @pyqtSlot()
    def params_clicked_slot(self):
        self.main_window_display_control.params_button_clicked()

    @pyqtSlot()
    def select_image_slot(self):
        self.image_selected_event.set()

    @pyqtSlot(bool)
    def show_hide_image_view_slot(self, show):
        if show:
            # Show the main image view
            self.ui.label_pix.show()
        else:
            # Hide the main image view
            self.ui.label_pix.hide()
            # self.ui.pushButton_back.raise_()

    @pyqtSlot()
    def images_dialog_close_slot(self):
        self.images_dialog_done_close_event.set()

    @pyqtSlot()
    def close_the_images_dialog_slot(self):
        self.close_the_image_dialog_event.set()

    @pyqtSlot(np.ndarray)
    def numpy_array_image_histogram_plot_slot(self, image):
        plot_image_histogram(self.ui.widget_histogram, image)
