import os
from PyQt6.QtWidgets import QGraphicsOpacityEffect

import globals
from HistogramPlot import plot_image_histogram
from PowerSaveTimerThread import restart_power_save_timer, enable_power_save_mode, disable_power_save_mode


class ParametersConfigurationSettingsGuiManager:
    """ This class manages the parameters setting GUI """

    def __init__(self, ui, conf_mssg_q, resume_grab_event, enable_param_setting_preview_event,
                 user_activity_event, focus_meas, configuration_manager):
        self.display = ui
        self.resume_frame_grabbing_event = resume_grab_event
        self.enable_param_setting_preview_event = enable_param_setting_preview_event
        self.user_activity_event = user_activity_event
        self.focus_measure = focus_meas
        self.configuration_manager = configuration_manager
        # A Q that is used for transferring configuration messages to rge camera process
        self.configuration_messages_queue = conf_mssg_q

        self.last_selected_tab = 0
        self.active_slider = globals.ACTIVE_SLIDER_NONE

        self.on_screen_parameters_display_enabled = True
        self.live_setting_enabled = True

        self.opacity_effect_gain = QGraphicsOpacityEffect()
        self.opacity_effect_lux = QGraphicsOpacityEffect()
        self.opacity_effect_exp_time = QGraphicsOpacityEffect()
        self.opacity_effect_focus = QGraphicsOpacityEffect()

    def get_last_selected_tab(self):
        return self.last_selected_tab

    def get_on_screen_parameters_display_enable_state(self):
        return self.on_screen_parameters_display_enabled

    def get_live_setting_enable_state(self):
        return self.live_setting_enabled

    def on_back_push_button_pressed(self):
        self.active_slider = globals.ACTIVE_SLIDER_NONE
        print("Slider None")

    def send_camera_control_message(self, message):
        # print(message)
        if not self.configuration_messages_queue.full():
            self.configuration_messages_queue.put(message, block=False)

    def activate_common_slider(self, param_name_string="", slider_value=0, display_value=0,
                               min_val=0, max_val=100, tick_interval=10):
        # self.display.label_pix.show()
        self.display.tab_widget_params.hide()
        self.display.widget_images.hide()
        self.display.widget_interfaces.hide()
        self.display.widget_hw.hide()
        self.display.pushButton_back.raise_()
        self.display.horizontalSlider_params_active.setRange(min_val, max_val)
        self.display.horizontalSlider_params_active.setValue(slider_value)
        self.display.horizontalSlider_params_active.setTickInterval(tick_interval)
        self.display.horizontalSlider_params_active.show()
        self.display.label_param_active_name.show()
        self.display.label_param_active_name.setText(param_name_string)
        self.display.lineEdit_parms_active.show()
        self.display.lineEdit_parms_active.setText(str(display_value))

        self.resume_frame_grabbing_event.set()
        self.enable_param_setting_preview_event.set()
        # self.camera_states.set_state(self.camera_states.STATE_SHOW_PREVIEW)

    def init_configuration_params_display(self):
        """"""
        self.display.tab_widget_params.currentChanged.connect(self.on_params_tab_change)

        self.display.horizontalSlider_params_active.hide()

        self.display.comboBox_params1_aec_agc_enable.addItem("Auto")
        self.display.comboBox_params1_aec_agc_enable.addItem("Manual")
        self.display.comboBox_params1_aec_agc_enable.currentIndexChanged.connect(self.on_aec_agc_mode_change)

        self.display.comboBox_params1_aec_agc_constraint_mode.addItem("Normal")
        self.display.comboBox_params1_aec_agc_constraint_mode.addItem("Highlights")
        self.display.comboBox_params1_aec_agc_constraint_mode.addItem("Shadows")
        self.display.comboBox_params1_aec_agc_constraint_mode.addItem("Custom*")
        self.display.comboBox_params1_aec_agc_constraint_mode.currentIndexChanged.connect(
            self.on_agc_aec_constraint_mode_change)

        self.display.comboBox_params1_aec_agc_exposure_mode.addItem("Normal")
        self.display.comboBox_params1_aec_agc_exposure_mode.addItem("Short")
        self.display.comboBox_params1_aec_agc_exposure_mode.addItem("Long")
        self.display.comboBox_params1_aec_agc_exposure_mode.addItem("Custom*")
        self.display.comboBox_params1_aec_agc_exposure_mode.currentIndexChanged.connect(
            self.on_agc_aec_exposure_mode_change)

        self.display.lineEdit_params1_exposure_time.setText("1000")
        self.display.lineEdit_params1_exposure_time.setEnabled(False)
        self.display.horizontalSlider_params1_exposure_time.valueChanged.connect(
            self.on_exposure_time_change)
        self.display.horizontalSlider_params1_exposure_time.setEnabled(False)

        self.display.lineEdit_params1_analog_gain.setText("1.0")
        self.display.lineEdit_params1_analog_gain.setEnabled(False)
        self.display.horizontalSlider_params1_analog_gain.valueChanged.connect(
            self.on_gain_change)
        self.display.horizontalSlider_params1_analog_gain.setEnabled(False)

        self.display.horizontalSlider_params1_exposure_compensation.valueChanged.connect(
            self.on_exposure_compensation_change)
        self.display.lineEdit_params1_exposure_compensation.setText("0")

        self.display.comboBox_params1_aec_agc_metering_mode.addItem("Center Weighted")
        self.display.comboBox_params1_aec_agc_metering_mode.addItem("Spot")
        self.display.comboBox_params1_aec_agc_metering_mode.addItem("Matrix")
        self.display.comboBox_params1_aec_agc_metering_mode.addItem("Custom*")
        self.display.comboBox_params1_aec_agc_metering_mode.currentIndexChanged.connect(
            self.on_aec_agc_metering_mode_change)

        self.display.comboBox_params2_awb_enable.addItem("Enabled")
        self.display.comboBox_params2_awb_enable.addItem("Disabled")
        self.display.comboBox_params2_awb_enable.currentIndexChanged.connect(
            self.on_awb_enable_change)

        self.display.comboBox_params2_white_balance_mode.addItem("Auto")
        self.display.comboBox_params2_white_balance_mode.addItem("Tungsten")
        self.display.comboBox_params2_white_balance_mode.addItem("Fluorescent")
        self.display.comboBox_params2_white_balance_mode.addItem("Indoor")
        self.display.comboBox_params2_white_balance_mode.addItem("Daylight")
        self.display.comboBox_params2_white_balance_mode.addItem("Cloudy")
        self.display.comboBox_params2_white_balance_mode.addItem("Custom*")
        self.display.comboBox_params2_white_balance_mode.setEnabled(True)  # auto WB is enabled as default
        self.display.comboBox_params2_white_balance_mode.currentIndexChanged.connect(
            self.on_white_balance_mode_change)

        self.display.lineEdit_params2_saturation.setText("1.0")
        self.display.horizontalSlider_params2_saturation.valueChanged.connect(self.on_saturation_change)

        self.display.lineEdit_params2_sharpness.setText("1.0")
        self.display.horizontalSlider_params2_sharpness.valueChanged.connect(self.on_sharpness_change)

        self.display.comboBox_params2_noise_reduction_mode.addItem("Off")
        self.display.comboBox_params2_noise_reduction_mode.addItem("Fast")
        self.display.comboBox_params2_noise_reduction_mode.addItem("High Quality")
        self.display.comboBox_params2_noise_reduction_mode.currentIndexChanged.connect(
            self.on_noise_reduction_mode_change)

        self.display.lineEdit_params2_contrast.setText("1.0")
        self.display.horizontalSlider_params2_contrast.valueChanged.connect(self.on_contrast_change)

        self.display.lineEdit_params2_brightness.setText("0.0")
        self.display.horizontalSlider_params2_brightness.valueChanged.connect(self.on_brightness_change)

        self.display.lineEdit_params2_quality.setText("80")
        self.display.horizontalSlider_params2_quality.valueChanged.connect(self.on_quality_change)

        self.display.comboBox_params4_on_screen_parameters.addItem("Enable")
        self.display.comboBox_params4_on_screen_parameters.addItem("Disable")
        self.display.comboBox_params4_on_screen_parameters.currentIndexChanged.connect(
            self.on_on_screen_parameters_change)

        self.opacity_effect_exp_time.setOpacity(0.4)
        self.display.label_param_exp_time_display.setStyleSheet("background-color: lightyellow")
        self.display.label_param_exp_time_display.setGraphicsEffect(self.opacity_effect_exp_time)

        self.opacity_effect_lux.setOpacity(0.4)
        self.display.label_param_lux_display.setStyleSheet("background-color: lightyellow")
        self.display.label_param_lux_display.setGraphicsEffect(self.opacity_effect_lux)

        self.opacity_effect_gain.setOpacity(0.4)
        self.display.label_param_gain_display.setStyleSheet("background-color: lightyellow")
        self.display.label_param_gain_display.setGraphicsEffect(self.opacity_effect_gain)

        self.opacity_effect_focus.setOpacity(0.4)
        self.display.label_param_focus_display.setStyleSheet("background-color: lightyellow")
        self.display.label_param_focus_display.setGraphicsEffect(self.opacity_effect_focus)

        self.display.comboBox_params4_live_setting.addItem("Enable")
        self.display.comboBox_params4_live_setting.addItem("Disable")
        self.display.comboBox_params4_live_setting.currentIndexChanged.connect(self.on_live_setting_change)

        self.display.comboBox_params4_focus_mode.addItem("None")
        self.display.comboBox_params4_focus_mode.addItem("Center 50x50")
        self.display.comboBox_params4_focus_mode.addItem("Center 100x100")
        self.display.comboBox_params4_focus_mode.addItem("Center 200x200")
        self.display.comboBox_params4_focus_mode.setCurrentIndex(globals.FOCUS_TYPE_CENTER_100X100)
        self.display.comboBox_params4_focus_mode.currentIndexChanged.connect(self.on_focus_mode_change)

        self.display.comboBox_params1_transform.addItem("None")
        self.display.comboBox_params1_transform.addItem("H Flip Horizontal Mirror")
        self.display.comboBox_params1_transform.addItem("V Flip     U<->D")
        self.display.comboBox_params1_transform.addItem("H+V Flip   Rotate 180")
        self.display.comboBox_params1_transform.currentIndexChanged.connect(self.on_pic_transform_change)

        self.display.comboBox_params4_shoot_delay_mode.addItem("None")
        self.display.comboBox_params4_shoot_delay_mode.addItem("2 Sec")
        self.display.comboBox_params4_shoot_delay_mode.addItem("5 Sec")
        self.display.comboBox_params4_shoot_delay_mode.addItem("10 Sec")
        self.display.comboBox_params4_shoot_delay_mode.addItem("15 Sec")
        self.display.comboBox_params4_shoot_delay_mode.currentIndexChanged.connect(self.on_shoot_delay_change)

        self.display.comboBox_params4_shoot_delay_beeps.addItem("OFF")
        self.display.comboBox_params4_shoot_delay_beeps.addItem("Ongoing")
        self.display.comboBox_params4_shoot_delay_beeps.addItem("Start Stop")
        self.display.comboBox_params4_shoot_delay_beeps.currentIndexChanged.connect(self.on_shoot_delay_beeps_change)

        self.display.comboBox_params4_exposure_beeps.addItem("OFF")
        self.display.comboBox_params4_exposure_beeps.addItem("End")
        self.display.comboBox_params4_exposure_beeps.addItem("Start")
        self.display.comboBox_params4_exposure_beeps.addItem("Start + End")
        self.display.comboBox_params4_exposure_beeps.currentIndexChanged.connect(self.on_exposure_beeps_change)

        self.display.comboBox_params4_preview_fps.addItem("30 fps")
        self.display.comboBox_params4_preview_fps.addItem("15 fps")
        self.display.comboBox_params4_preview_fps.addItem("10 fps")
        # self.display.comboBox_params4_preview_fps.addItem("5 fps")
        # self.display.comboBox_params4_preview_fps.addItem("1 fps")
        self.display.comboBox_params4_preview_fps.addItem("Stills")
        self.display.comboBox_params4_preview_fps.currentIndexChanged.connect(self.on_preview_fps_change)

        self.display.comboBox_params4_histogram.addItem("Off")
        self.display.comboBox_params4_histogram.addItem("On")
        self.display.comboBox_params4_histogram.currentIndexChanged.connect(self.on_show_histogram_change)

        self.display.comboBox_params5_flash_mode.addItem("Disabled")
        self.display.comboBox_params5_flash_mode.addItem("Front")
        self.display.comboBox_params5_flash_mode.addItem("Back")
        self.display.comboBox_params5_flash_mode.currentIndexChanged.connect(self.on_flash_mode_change)

        self.display.comboBox_params5_flash_delay.addItem("None")
        self.display.comboBox_params5_flash_delay.addItem("0.1 Sec")
        self.display.comboBox_params5_flash_delay.addItem("0.2 Sec")
        self.display.comboBox_params5_flash_delay.addItem("0.5 Sec")
        self.display.comboBox_params5_flash_delay.addItem("1 Sec")
        self.display.comboBox_params5_flash_delay.addItem("2 Sec")
        self.display.comboBox_params5_flash_delay.addItem("5 Sec")
        self.display.comboBox_params5_flash_delay.currentIndexChanged.connect(self.on_flash_delay_change)
        self.display.comboBox_params5_flash_delay.setEnabled(False)

        self.display.comboBox_params6_powerup_config_mode.addItem("Last")
        self.display.comboBox_params6_powerup_config_mode.addItem("Default")
        self.display.comboBox_params6_powerup_config_mode.currentIndexChanged.connect(
            self.on_powerup_configuration_mode_change)

        self.display.comboBox_web_server.addItem("Disabled")
        self.display.comboBox_web_server.addItem("Enabled (http://IP:5000)")
        self.display.comboBox_web_server.currentIndexChanged.connect(self.on_web_server_change)

        self.display.comboBox_params6_power_save_timer.addItem("1 min")
        self.display.comboBox_params6_power_save_timer.addItem("2 min")
        self.display.comboBox_params6_power_save_timer.addItem("5 min")
        self.display.comboBox_params6_power_save_timer.addItem("10 min")
        self.display.comboBox_params6_power_save_timer.addItem("Disabled")
        self.display.comboBox_params6_power_save_timer.currentIndexChanged.connect(self.on_power_save_timer_mode_change)

        self.display.horizontalSlider_params_active.valueChanged.connect(self.on_common_active_slider_change)

    def on_common_active_slider_change(self, i):
        if self.active_slider == globals.ACTIVE_SLIDER_EXPOSURE_TIME:
            self.display.horizontalSlider_params1_exposure_time.setValue(i)
            self.on_exposure_time_change(i)

        elif self.active_slider == globals.ACTIVE_SLIDER_GAIN:
            self.display.horizontalSlider_params1_analog_gain.setValue(i)
            self.on_gain_change(i)

        elif self.active_slider == globals.ACTIVE_SLIDER_EXPOSURE_COMPENSATION:
            self.display.horizontalSlider_params1_exposure_compensation.setValue(i)
            self.on_exposure_compensation_change(i)

        elif self.active_slider == globals.ACTIVE_SLIDER_SATURATION:
            self.display.horizontalSlider_params2_saturation.setValue(i)
            self.on_saturation_change(i)

        elif self.active_slider == globals.ACTIVE_SLIDER_CONTRAST:
            self.display.horizontalSlider_params2_contrast.setValue(i)
            self.on_contrast_change(i)

        elif self.active_slider == globals.ACTIVE_SLIDER_BRIGHTNESS:
            self.display.horizontalSlider_params2_brightness.setValue(i)
            self.on_brightness_change(i)

        elif self.active_slider == globals.ACTIVE_SLIDER_SHARPNESS:
            self.display.horizontalSlider_params2_sharpness.setValue(i)
            self.on_sharpness_change(i)

        self.user_activity_event.set()

    def on_params_tab_change(self, i):
        self.last_selected_tab = i
        self.user_activity_event.set()

    def on_aec_agc_mode_change(self, i):
        # This function is defined as a Slot of the AGC mode combobox widget.
        # It is also called as part of the configuration setting procedure at powerup.
        # When called at powerup, the control shall also be set accordingly.
        self.display.comboBox_params1_aec_agc_enable.blockSignals(True)
        self.display.comboBox_params1_aec_agc_enable.setCurrentIndex(i)
        self.display.comboBox_params1_aec_agc_enable.blockSignals(False)

        auto_controls_enable = True

        print("on_aec_agc_mode_change ", i)

        if i in range(0, 2):
            agc_mode_message = globals.DEFAULT_CAMERA_CONTROL_AGC_MODE[:10] + f"{i:03d}"
            self.send_camera_control_message(agc_mode_message)

            self.configuration_manager.save_exposure_mode(i)

            if i == 0:  # Enabled
                auto_controls_enable = True
            elif i == 1:  # Disabled
                auto_controls_enable = False

            self.display.comboBox_params1_aec_agc_constraint_mode.setEnabled(auto_controls_enable)
            self.display.comboBox_params1_aec_agc_exposure_mode.setEnabled(auto_controls_enable)
            self.display.horizontalSlider_params1_exposure_compensation.setEnabled(auto_controls_enable)
            self.display.lineEdit_params1_exposure_compensation.setEnabled(auto_controls_enable)
            self.display.comboBox_params1_aec_agc_metering_mode.setEnabled(auto_controls_enable)

            self.display.horizontalSlider_params1_exposure_time.setDisabled(auto_controls_enable)
            self.display.lineEdit_params1_exposure_time.setDisabled(auto_controls_enable)
            self.display.horizontalSlider_params1_analog_gain.setDisabled(auto_controls_enable)
            self.display.lineEdit_params1_analog_gain.setDisabled(auto_controls_enable)

        self.user_activity_event.set()

    def on_agc_aec_constraint_mode_change(self, i):

        self.display.comboBox_params1_aec_agc_constraint_mode.blockSignals(True)
        self.display.comboBox_params1_aec_agc_constraint_mode.setCurrentIndex(i)
        self.display.comboBox_params1_aec_agc_constraint_mode.blockSignals(False)

        agc_constraint_mode_message = globals.DEFAULT_CAMERA_CONTROL_AGC_CONSTRAINT_MODE[:10] + f"{i:03d}"
        self.send_camera_control_message(agc_constraint_mode_message)

        self.configuration_manager.save_agc_constraints_mode(i)

        self.user_activity_event.set()

    def on_agc_aec_exposure_mode_change(self, i):

        self.display.comboBox_params1_aec_agc_exposure_mode.blockSignals(True)
        self.display.comboBox_params1_aec_agc_exposure_mode.setCurrentIndex(i)
        self.display.comboBox_params1_aec_agc_exposure_mode.blockSignals(False)

        agc_exposure_mode_message = globals.DEFAULT_CAMERA_CONTROL_AGC_EXPOSURE_MODE[:10] + f"{i:03d}"
        self.send_camera_control_message(agc_exposure_mode_message)

        self.configuration_manager.save_agc_exposure_mode(i)

        self.user_activity_event.set()

    def on_exposure_time_change(self, i):

        self.display.horizontalSlider_params1_exposure_time.blockSignals(True)
        self.display.horizontalSlider_params1_exposure_time.setValue(i)
        self.display.horizontalSlider_params1_exposure_time.blockSignals(False)

        self.set_exposure_time_display_value(i)

        if self.live_setting_enabled:
            if not self.active_slider == globals.ACTIVE_SLIDER_EXPOSURE_TIME:
                self.active_slider = globals.ACTIVE_SLIDER_EXPOSURE_TIME
                self.activate_common_slider("Exposure Time", i,
                                            globals.exposure_display_values[i],
                                            0, 54, 5)

            self.display.lineEdit_parms_active.setText(globals.exposure_display_values[i])

        exposure_time_message = globals.DEFAULT_CAMERA_CONTROL_EXPOSURE_TIME[:10] + f"{i:03d}"
        self.send_camera_control_message(exposure_time_message)

        self.configuration_manager.save_exposure_time(i)

        self.user_activity_event.set()

    def on_gain_change(self, i):

        self.display.horizontalSlider_params1_analog_gain.blockSignals(True)
        self.display.horizontalSlider_params1_analog_gain.setValue(i)
        self.display.horizontalSlider_params1_analog_gain.blockSignals(False)

        gain = i / 10
        self.set_gain_display_value(gain)

        if self.live_setting_enabled:
            if not self.active_slider == globals.ACTIVE_SLIDER_GAIN:
                self.active_slider = globals.ACTIVE_SLIDER_GAIN
                self.activate_common_slider("Gain", i, gain,
                                            10, 80, 10)

            self.display.lineEdit_parms_active.setText(str(gain))

        gain_message = globals.DEFAULT_CAMERA_CONTROL_GAIN[:10] + f"{i:03d}"
        self.send_camera_control_message(gain_message)

        self.configuration_manager.save_analog_gain(i)

        self.user_activity_event.set()

    def on_exposure_compensation_change(self, i):

        self.display.horizontalSlider_params1_exposure_compensation.blockSignals(True)
        self.display.horizontalSlider_params1_exposure_compensation.setValue(i)
        self.display.horizontalSlider_params1_exposure_compensation.blockSignals(False)

        exp_comp = i
        self.set_exposure_compensation_display_value(exp_comp)

        if self.live_setting_enabled:
            if not self.active_slider == globals.ACTIVE_SLIDER_EXPOSURE_COMPENSATION:
                self.active_slider = globals.ACTIVE_SLIDER_EXPOSURE_COMPENSATION
                self.activate_common_slider("Exposure Compensation", i, exp_comp,
                                            -8, 8, 1)

            self.display.lineEdit_parms_active.setText(str(exp_comp))

        exposure_compensation_message = globals.DEFAULT_CAMERA_CONTROL_EXPOSURE_COMPENSATION[:10] + f"{i:03d}"
        self.send_camera_control_message(exposure_compensation_message)

        self.configuration_manager.save_agc_exposure_mode(i)

        self.user_activity_event.set()

    def on_aec_agc_metering_mode_change(self, i):

        self.display.comboBox_params1_aec_agc_metering_mode.blockSignals(True)
        self.display.comboBox_params1_aec_agc_metering_mode.setCurrentIndex(i)
        self.display.comboBox_params1_aec_agc_metering_mode.blockSignals(False)

        agc_metering_mode_message = globals.DEFAULT_CAMERA_CONTROL_AGC_METERING_MODE[:10] + f"{i:03d}"
        self.send_camera_control_message(agc_metering_mode_message)

        self.configuration_manager.save_agc_metering_mode(i)

        self.user_activity_event.set()

    def on_awb_enable_change(self, i):

        self.display.comboBox_params2_awb_enable.blockSignals(True)
        self.display.comboBox_params2_awb_enable.setCurrentIndex(i)
        self.display.comboBox_params2_awb_enable.blockSignals(False)

        if i == 0:
            # AWB is enabled
            self.display.comboBox_params2_white_balance_mode.setEnabled(True)
        else:
            # AWB is disabled
            self.display.comboBox_params2_white_balance_mode.setEnabled(False)

        awb_enable_message = globals.DEFAULT_CAMERA_CONTROL_AWB_ENABLE[:10] + f"{i:03d}"
        self.send_camera_control_message(awb_enable_message)

        self.configuration_manager.save_auto_white_balance_enabled(i)

        self.user_activity_event.set()

    def on_white_balance_mode_change(self, i):

        self.display.comboBox_params2_white_balance_mode.blockSignals(True)
        self.display.comboBox_params2_white_balance_mode.setCurrentIndex(i)
        self.display.comboBox_params2_white_balance_mode.blockSignals(False)

        white_balance_mode_message = globals.DEFAULT_CAMERA_CONTROL_WB_MODE[:10] + f"{i:03d}"
        self.send_camera_control_message(white_balance_mode_message)

        self.configuration_manager.save_auto_white_balance_mode(i)

        self.user_activity_event.set()

    def on_saturation_change(self, i):

        self.display.horizontalSlider_params2_saturation.blockSignals(True)
        self.display.horizontalSlider_params2_saturation.setValue(i)
        self.display.horizontalSlider_params2_saturation.blockSignals(False)

        if i in range(0, 41):  # Saturation range of 0-32 is too large
            sat = i / 10
            self.set_saturation_display_value(sat)

            if self.live_setting_enabled:
                if not self.active_slider == globals.ACTIVE_SLIDER_SATURATION:
                    self.active_slider = globals.ACTIVE_SLIDER_SATURATION
                    self.activate_common_slider("Saturation", i, sat, 0, 40, 4)

                self.display.lineEdit_parms_active.setText(str(sat))

            sat_message = globals.DEFAULT_CAMERA_CONTROL_SATURATION[:10] + f"{i:03d}"
            self.send_camera_control_message(sat_message)

            self.configuration_manager.save_color_saturation(i)

            self.user_activity_event.set()

    def on_sharpness_change(self, i):

        self.display.horizontalSlider_params2_sharpness.blockSignals(True)
        self.display.horizontalSlider_params2_sharpness.setValue(i)
        self.display.horizontalSlider_params2_sharpness.blockSignals(False)

        sharpness = i / 10
        self.set_sharpness_display_value(sharpness)

        if self.live_setting_enabled:
            if not self.active_slider == globals.ACTIVE_SLIDER_SHARPNESS:
                self.active_slider = globals.ACTIVE_SLIDER_SHARPNESS
                self.activate_common_slider("Sharpness", i, sharpness, 0, 160, 16)

            self.display.lineEdit_parms_active.setText(str(sharpness))

        sharpness_message = globals.DEFAULT_CAMERA_CONTROL_SHARPNESS[:10] + f"{i:03d}"
        self.send_camera_control_message(sharpness_message)

        self.configuration_manager.save_sharpness_level(i)

        self.user_activity_event.set()

    def on_noise_reduction_mode_change(self, i):

        self.display.comboBox_params2_noise_reduction_mode.blockSignals(True)
        self.display.comboBox_params2_noise_reduction_mode.setCurrentIndex(i)
        self.display.comboBox_params2_noise_reduction_mode.blockSignals(False)

        noise_reduction_message = globals.DEFAULT_CAMERA_CONTROL_NOISE_REDUCTION_MODE[:10] + f"{i:03d}"
        self.send_camera_control_message(noise_reduction_message)

        self.configuration_manager.save_noise_reduction_mode(i)

        self.user_activity_event.set()

    def on_contrast_change(self, i):

        self.display.horizontalSlider_params2_contrast.blockSignals(True)
        self.display.horizontalSlider_params2_contrast.setValue(i)
        self.display.horizontalSlider_params2_contrast.blockSignals(False)

        contrast = i / 10  # Changed to 0-40
        self.set_contrast_display_value(contrast)

        if self.live_setting_enabled:
            if not self.active_slider == globals.ACTIVE_SLIDER_CONTRAST:
                self.active_slider = globals.ACTIVE_SLIDER_CONTRAST
                self.activate_common_slider("Contrast", i, contrast, 0, 40, 4)

            self.display.lineEdit_parms_active.setText(str(contrast))

        contrast_message = globals.DEFAULT_CAMERA_CONTROL_CONTRAST[:10] + f"{i:03d}"
        self.send_camera_control_message(contrast_message)

        self.configuration_manager.save_contrast_level(i)

        self.user_activity_event.set()

    def on_brightness_change(self, i):

        self.display.horizontalSlider_params2_brightness.blockSignals(True)
        self.display.horizontalSlider_params2_brightness.setValue(i)
        self.display.horizontalSlider_params2_brightness.blockSignals(False)

        brightness = i / 100
        self.set_brightness_display_value(brightness)

        if self.live_setting_enabled:
            if not self.active_slider == globals.ACTIVE_SLIDER_BRIGHTNESS:
                self.active_slider = globals.ACTIVE_SLIDER_BRIGHTNESS
                self.activate_common_slider("Brightness", i, brightness, -100, 100, 20)

            self.display.lineEdit_parms_active.setText(str(brightness))

        brightness_message = globals.DEFAULT_CAMERA_CONTROL_BRIGHTNESS[:10] + f"{i:03d}"
        self.send_camera_control_message(brightness_message)

        self.configuration_manager.save_brightness_level(i)

        self.user_activity_event.set()

    def on_quality_change(self, q):

        self.display.horizontalSlider_params2_quality.blockSignals(True)
        self.display.horizontalSlider_params2_quality.setValue(q)
        self.display.horizontalSlider_params2_quality.blockSignals(False)

        self.set_quality_display_value(q)

        quality_message = globals.DEFAULT_CAMERA_CONTROL_QUALITY[:10] + f"{q:03d}"
        self.send_camera_control_message(quality_message)

        self.configuration_manager.save_captured_image_quality(q)

        self.user_activity_event.set()

    def on_on_screen_parameters_change(self, i):

        self.display.comboBox_params4_on_screen_parameters.blockSignals(True)
        self.display.comboBox_params4_on_screen_parameters.setCurrentIndex(i)
        self.display.comboBox_params4_on_screen_parameters.blockSignals(False)

        if i == 0:
            self.on_screen_parameters_display_enabled = True
        elif i == 1:
            self.on_screen_parameters_display_enabled = False

        self.configuration_manager.save_on_screen_parameters_enabled(i)

        self.user_activity_event.set()

    def on_live_setting_change(self, i):

        self.display.comboBox_params4_live_setting.blockSignals(True)
        self.display.comboBox_params4_live_setting.setCurrentIndex(i)
        self.display.comboBox_params4_live_setting.blockSignals(False)

        if i == 0:
            self.live_setting_enabled = True
        elif i == 1:
            self.live_setting_enabled = False

        self.configuration_manager.save_live_settings_enabled(i)

        self.user_activity_event.set()

    def on_focus_mode_change(self, m):

        self.display.comboBox_params4_focus_mode.blockSignals(True)
        self.display.comboBox_params4_focus_mode.setCurrentIndex(m)
        self.display.comboBox_params4_focus_mode.blockSignals(False)

        self.focus_measure.set_focus_mode(m)

        self.configuration_manager.save_focus_measure_mode(m)

        self.user_activity_event.set()

    def on_pic_transform_change(self, i):

        self.display.comboBox_params1_transform.blockSignals(True)
        self.display.comboBox_params1_transform.setCurrentIndex(i)
        self.display.comboBox_params1_transform.blockSignals(False)

        transform_message = globals.DEFAULT_CAMERA_CONTROL_PIC_TRANSFORM[:10] + f"{i:03d}"
        self.send_camera_control_message(transform_message)

        self.configuration_manager.save_display_transform_mode(i)

        self.user_activity_event.set()

    def on_shoot_delay_change(self, i):

        self.display.comboBox_params4_shoot_delay_mode.blockSignals(True)
        self.display.comboBox_params4_shoot_delay_mode.setCurrentIndex(i)
        self.display.comboBox_params4_shoot_delay_mode.blockSignals(False)

        shoot_delay_message = globals.DEFAULT_CAMERA_CONTROL_SHOOT_DELAY[:10] + f"{i:03d}"
        self.send_camera_control_message(shoot_delay_message)

        self.configuration_manager.save_shoot_delay_timer_mode(i)

        self.user_activity_event.set()

    def on_shoot_delay_beeps_change(self, i):

        self.display.comboBox_params4_shoot_delay_beeps.blockSignals(True)
        self.display.comboBox_params4_shoot_delay_beeps.setCurrentIndex(i)
        self.display.comboBox_params4_shoot_delay_beeps.blockSignals(False)

        shoot_delay_beeps_message = globals.DEFAULT_CAMERA_CONTROL_SHOOT_DELAY_BEEPS[:10] + f"{i:03d}"
        self.send_camera_control_message(shoot_delay_beeps_message)

        self.configuration_manager.save_shoot_delay_beeps_mode(i)

        self.user_activity_event.set()

    def on_exposure_beeps_change(self, i):

        self.display.comboBox_params4_exposure_beeps.blockSignals(True)
        self.display.comboBox_params4_exposure_beeps.setCurrentIndex(i)
        self.display.comboBox_params4_exposure_beeps.blockSignals(False)

        exposure_beeps_message = globals.DEFAULT_CAMERA_CONTROL_EXPOSURE_BEEPS[:10] + f"{i:03d}"
        self.send_camera_control_message(exposure_beeps_message)

        self.user_activity_event.set()

    def on_preview_fps_change(self, fps):

        self.display.comboBox_params4_preview_fps.blockSignals(True)
        self.display.comboBox_params4_preview_fps.setCurrentIndex(fps)
        self.display.comboBox_params4_preview_fps.blockSignals(False)

        preview_fps_message = globals.DEFAULT_CAMERA_CONTROL_PREVIEW_FPS[:10] + f"{fps:03d}"
        self.send_camera_control_message(preview_fps_message)

        self.configuration_manager.save_preview_frame_rate(fps)

        self.user_activity_event.set()

    def on_show_histogram_change(self, s):

        self.display.comboBox_params4_histogram.blockSignals(True)
        self.display.comboBox_params4_histogram.setCurrentIndex(s)
        self.display.comboBox_params4_histogram.blockSignals(False)

        if s == 0:
            # Off
            self.display.widget_histogram.hide()
        elif s == 1:
            # On
            self.display.widget_histogram.show()

        self.configuration_manager.save_show_histogram_enabled(s)

        self.user_activity_event.set()

    def on_flash_mode_change(self, m):

        self.display.comboBox_params5_flash_mode.blockSignals(True)
        self.display.comboBox_params5_flash_mode.setCurrentIndex(m)
        self.display.comboBox_params5_flash_mode.blockSignals(False)

        flash_mode_message = globals.DEFAULT_CAMERA_CONTROL_FLASH_MODE[:10] + f"{m:03d}"
        self.send_camera_control_message(flash_mode_message)

        if m == 0:
            # Flash is not active - disable flash delay combo.
            self.display.comboBox_params5_flash_delay.setDisabled(True)
        else:
            self.display.comboBox_params5_flash_delay.setEnabled(True)

        self.configuration_manager.save_flash_mode(m)

        self.user_activity_event.set()

    def on_flash_delay_change(self, d):

        self.display.comboBox_params5_flash_delay.blockSignals(True)
        self.display.comboBox_params5_flash_delay.setCurrentIndex(d)
        self.display.comboBox_params5_flash_delay.blockSignals(False)

        flash_delay_message = globals.DEFAULT_CAMERA_CONTROL_FLASH_DELAY[:10] + f"{d:03d}"
        self.send_camera_control_message(flash_delay_message)

        self.user_activity_event.set()

    def on_powerup_configuration_mode_change(self, cm):
        self.configuration_manager.set_powerup_configuration_mode(cm)

        self.user_activity_event.set()

    def on_power_save_timer_mode_change(self, pstm):

        # It is here so if the Disabled option is selected, it will not restart the timer
        self.user_activity_event.set()

        self.display.comboBox_params6_power_save_timer.blockSignals(True)
        self.display.comboBox_params6_power_save_timer.setCurrentIndex(pstm)
        self.display.comboBox_params6_power_save_timer.blockSignals(False)

        if pstm == globals.POWER_SAVE_TIMER_MODE_1_MIN:
            restart_power_save_timer(60)
            enable_power_save_mode()
        elif pstm == globals.POWER_SAVE_TIMER_MODE_2_MIN:
            restart_power_save_timer(120)
            enable_power_save_mode()
        elif pstm == globals.POWER_SAVE_TIMER_MODE_5_MIN:
            restart_power_save_timer(300)
            enable_power_save_mode()
        elif pstm == globals.POWER_SAVE_TIMER_MODE_10_MIN:
            restart_power_save_timer(600)
            enable_power_save_mode()
        elif pstm == globals.POWER_SAVE_TIMER_MODE_DISABLED:
            disable_power_save_mode()

        self.configuration_manager.save_power_save_timeout(pstm)

    def on_web_server_change(self, i):
        if i == globals.WEB_SERVER_ENABLED:
            os.system("python3 WebServerService.py &")
        else:
            # currently disabling the server is not supported
            pass

        self.user_activity_event.set()

    def set_exposure_time_display_value(self, exp):
        self.display.lineEdit_params1_exposure_time.setText(globals.exposure_display_values[exp])

    def set_gain_display_value(self, gain):
        self.display.lineEdit_params1_analog_gain.setText(str(gain))

    def set_exposure_compensation_display_value(self, exp_c):
        self.display.lineEdit_params1_exposure_compensation.setText(str(exp_c))

    def set_saturation_display_value(self, sat):
        self.display.lineEdit_params2_saturation.setText(str(sat))

    def set_sharpness_display_value(self, sharp):
        self.display.lineEdit_params2_sharpness.setText(str(sharp))

    def set_contrast_display_value(self, contrast):
        self.display.lineEdit_params2_contrast.setText(str(contrast))

    def set_brightness_display_value(self, bright):
        self.display.lineEdit_params2_brightness.setText(str(bright))

    def set_quality_display_value(self, q):
        self.display.lineEdit_params2_quality.setText(str(q))
