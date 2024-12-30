import time

import globals


class ConfigurationLoader:
    """ This class is used to load camera configuration and set camera setting parameters. """
    def __init__(self, configuration_manager, parameters_setting):
        self.configuration_manager = configuration_manager
        self.parameters_setting = parameters_setting
        self.configuration = {}

    def load_and_set_configuration(self):
        print("Loading and setting configuration parameters")
        self.configuration_manager.read_configuration()

        self.configuration['exposure_mode'] = self.configuration_manager.get_exposure_mode()
        self.configuration['agc_constraints_mode'] = self.configuration_manager.get_agc_constraints_mode()
        self.configuration['agc_exposure_mode'] = self.configuration_manager.get_agc_exposure_mode()
        self.configuration['agc_exposure_compensation'] = self.configuration_manager.get_agc_exposure_compensation()
        self.configuration['agc_metering_mode'] = self.configuration_manager.get_agc_metering_mode()
        self.configuration['exposure_time'] = self.configuration_manager.get_exposure_time()
        self.configuration['analog_gain'] = self.configuration_manager.get_analog_gain()
        self.configuration['auto_white_balance_enabled'] = self.configuration_manager.get_auto_white_balance_enabled()
        self.configuration['auto_white_balance_mode'] = self.configuration_manager.get_auto_white_balance_mode()
        self.configuration['color_saturation'] = self.configuration_manager.get_color_saturation()
        self.configuration['sharpness_level'] = self.configuration_manager.get_sharpness_level()
        self.configuration['noise_reduction_mode'] = self.configuration_manager.get_noise_reduction_mode()
        self.configuration['contrast_level'] = self.configuration_manager.get_contrast_level()
        self.configuration['brightness_level'] = self.configuration_manager.get_brightness_level()
        self.configuration['captured_image_quality'] = self.configuration_manager.get_captured_image_quality()
        self.configuration['shoot_delay_timer_mode'] = self.configuration_manager.get_shoot_delay_timer_mode()
        self.configuration['shoot_delay_beeps_mode'] = self.configuration_manager.get_shoot_delay_beeps_mode()
        self.configuration['on_screen_parameters_enabled'] = (
            self.configuration_manager.get_on_screen_parameters_enabled())
        self.configuration['live_settings_enabled'] = self.configuration_manager.get_live_settings_enabled()
        self.configuration['focus_measure_mode'] = self.configuration_manager.get_focus_measure_mode()
        self.configuration['preview_frame_rate'] = self.configuration_manager.get_preview_frame_rate()
        self.configuration['show_histogram_enabled'] = self.configuration_manager.get_show_histogram_enabled()
        self.configuration['display_transform_mode'] = self.configuration_manager.get_display_transform_mode()
        self.configuration['flash_mode'] = self.configuration_manager.get_flash_mode()
        self.configuration['flash_delay'] = self.configuration_manager.get_flash_delay()
        self.configuration['power_save_timeout'] = self.configuration_manager.get_power_save_timeout()

        print("Loaded configuration ", self.configuration)

        self._set_camera_parameters()

    def _set_camera_parameters(self):
        delay_sec = 0.1
        # self.parameters_setting.on_aec_agc_mode_change(self.configuration['exposure_mode'])
        # self.parameters_setting.on_awb_enable_change(self.configuration['auto_white_balance_enabled'])

        # Temporarily disable live setting
        self.parameters_setting.on_live_setting_change(globals.ON_SCREEN_PARAMS_DISABLED)

        self.parameters_setting.on_agc_aec_constraint_mode_change(self.configuration['agc_constraints_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_agc_aec_exposure_mode_change(self.configuration['agc_exposure_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_exposure_compensation_change(self.configuration['agc_exposure_compensation'])
        time.sleep(delay_sec)
        self.parameters_setting.on_aec_agc_metering_mode_change(self.configuration['agc_metering_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_exposure_time_change(self.configuration['exposure_time'])
        time.sleep(delay_sec)
        self.parameters_setting.on_gain_change(self.configuration['analog_gain'])
        time.sleep(delay_sec)
        self.parameters_setting.on_white_balance_mode_change(self.configuration['auto_white_balance_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_saturation_change(self.configuration['color_saturation'])
        time.sleep(delay_sec)
        self.parameters_setting.on_sharpness_change(self.configuration['sharpness_level'])
        time.sleep(delay_sec)
        self.parameters_setting.on_noise_reduction_mode_change(self.configuration['noise_reduction_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_contrast_change(self.configuration['contrast_level'])
        time.sleep(delay_sec)
        self.parameters_setting.on_brightness_change(self.configuration['brightness_level'])
        time.sleep(delay_sec)
        self.parameters_setting.on_quality_change(self.configuration['captured_image_quality'])
        time.sleep(delay_sec)
        self.parameters_setting.on_shoot_delay_change(self.configuration['shoot_delay_timer_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_shoot_delay_beeps_change(self.configuration['shoot_delay_beeps_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_on_screen_parameters_change(self.configuration['on_screen_parameters_enabled'])
        time.sleep(delay_sec)
        self.parameters_setting.on_live_setting_change(self.configuration['live_settings_enabled'])
        time.sleep(delay_sec)
        self.parameters_setting.on_focus_mode_change(self.configuration['focus_measure_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_preview_fps_change(self.configuration['preview_frame_rate'])
        time.sleep(delay_sec)
        self.parameters_setting.on_show_histogram_change(self.configuration['show_histogram_enabled'])
        time.sleep(delay_sec)
        self.parameters_setting.on_pic_transform_change(self.configuration['display_transform_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_flash_mode_change(self.configuration['flash_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_flash_delay_change(self.configuration['flash_delay'])
        time.sleep(delay_sec)
        self.parameters_setting.on_power_save_timer_mode_change(self.configuration['power_save_timeout'])
        time.sleep(delay_sec)

        # These settings should be set last agan
        self.parameters_setting.on_aec_agc_mode_change(self.configuration['exposure_mode'])
        time.sleep(delay_sec)
        self.parameters_setting.on_awb_enable_change(self.configuration['auto_white_balance_enabled'])
        time.sleep(delay_sec)
