import time
from configparser import ConfigParser

import globals


class ConfigurationManager:
    """ This class handles the configuration management of the camera.
        The camera configuration includes the setting parameters of the camera.
        When a setting parameter is changed, its configuration value is also changed.
        When a new image is captured, the configuration data is stored if it was changed since the last time.
        At powerup, all the setting parameters are set according to the configuration data.
        Based on the powerup configuration mode: Default-mode - the configuration default values are used;
        Last-mode - the last updated configuration values are used.
        The current configuration parameters may be saved as the default configuration parameters. """

    def __init__(self, file_name):
        self.parser = ConfigParser()

        self.configuration_file_name = file_name
        self.parser.read(self.configuration_file_name)

        self.last_image_file_index = self.parser.get('image_files', 'last_image_files_last_index')
        self.max_image_file_index = self.parser.get('image_files', 'max_image_files_index')

        #self.powerup_configuration_mode = globals.DEFAULT_POWER_UP_CONFIGURATION
        # True when the configuration was changed from the last time it was save.
        self.last_configuration_changed = False

        self.configuration = {}

        self.get_powerup_configuration_mode()

    def set_configuration_was_changed(self, update_configuration_file=False):
        """ Used to indicate that the configuration was changed since it was last saved """
        self.last_configuration_changed = True
        if update_configuration_file:
            self.save_configuration()
            self.set_last_configuration_was_saved()

    def get_configuration_was_changed(self):
        return self.last_configuration_changed

    def set_last_configuration_was_saved(self):
        """ Used to indicate that the last configuration was saved """
        self.last_configuration_changed = False

    def read_configuration(self, read_and_set=False):
        self.parser.read(self.configuration_file_name)
        return self.parser

    def save_configuration(self):
        with open(self.configuration_file_name, 'w') as config_file:
            self.parser.write(config_file)

    def get_powerup_configuration_mode(self):
        pcm = self.parser['configuration']['powerup_configuration']
        if pcm == 'last':
            self.powerup_configuration_mode = globals.POWER_UP_CONFIGURATION_LAST
            return globals.POWER_UP_CONFIGURATION_LAST
        elif pcm == 'default':
            self.powerup_configuration_mode = globals.POWER_UP_CONFIGURATION_DEFAULT
            return globals.POWER_UP_CONFIGURATION_DEFAULT
        else:
            return globals.DEFAULT_POWER_UP_CONFIGURATION

    def set_powerup_configuration_mode(self, pcm):
        if pcm == globals.POWER_UP_CONFIGURATION_LAST:
            self.parser['configuration']['powerup_configuration'] = 'last'
            print("Configuration Mode set to Last")
            self.set_configuration_was_changed(update_configuration_file=True)
        elif pcm == globals.POWER_UP_CONFIGURATION_DEFAULT:
            self.parser['configuration']['powerup_configuration'] = 'default'
            print("Configuration Mode set to Default")
            self.set_configuration_was_changed(update_configuration_file=True)

    def get_exposure_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            em = self.parser['params-exposure']['exposure_mode']
        else:
            em = self.parser['DEFAULT']['exposure_mode']

        if em == 'auto':
            return globals.AGC_MODE_AUTO
        elif em == 'manual':
            return globals.AGC_MODE_MANUAL
        else:
            return globals.AGC_MODE_DEFAULT

    def save_exposure_mode(self, em, is_default=False):
        if not is_default :
            section = 'params-exposure'
        else:
            section = 'DEFAULT'

        if em == globals.AGC_MODE_AUTO:
            self.parser[section]['exposure_mode'] = 'auto'
        elif em == globals.AGC_MODE_MANUAL:
            self.parser[section]['exposure_mode'] = 'manual'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_agc_constraints_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            cm = self.parser['params-exposure']['agc_constraints_mode']
        else:
            cm = self.parser['DEFAULT']['agc_constraints_mode']

        if cm == 'normal':
            return globals.AGC_CONSTRAINT_MODE_NORMAL
        elif cm == 'highlight':
            return globals.AGC_CONSTRAINT_MODE_HIGHLIGHT
        elif cm == 'shadows':
            return globals.AGC_CONSTRAINT_MODE_SHADOWS
        elif cm == 'custom':
            return globals.AGC_CONSTRAINT_MODE_CUSTOM
        else:
            return globals.AGC_CONSTRAINT_MODE_DEFAULT

    def save_agc_constraints_mode(self, cm, is_default=False):
        if not is_default:
            section = 'params-exposure'
        else:
            section = 'DEFAULT'

        if cm == globals.AGC_CONSTRAINT_MODE_NORMAL:
            self.parser[section]['agc_constraints_mode'] = 'normal'
        elif cm == globals.AGC_CONSTRAINT_MODE_HIGHLIGHT:
            self.parser[section]['agc_constraints_mode'] = 'highlight'
        elif cm == globals.AGC_CONSTRAINT_MODE_SHADOWS:
            self.parser[section]['agc_constraints_mode'] = 'shadows'
        elif cm == globals.AGC_CONSTRAINT_MODE_CUSTOM:
            self.parser[section]['agc_constraints_mode'] = 'custom'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_agc_exposure_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            em = self.parser['params-exposure']['agc_exposure_mode']
        else:
            em = self.parser['DEFAULT']['agc_exposure_mode']

        if em == 'normal':
            return globals.AGC_EXPOSURE_MODE_NORMAL
        elif em == 'short':
            return globals.AGC_EXPOSURE_MODE_SHORT
        elif em == 'long':
            return globals.AGC_EXPOSURE_MODE_LONG
        elif em == 'custom':
            return globals.AGC_EXPOSURE_MODE_CUSTOM
        else:
            return globals.AGC_EXPOSURE_MODE_DEFAULT

    def save_agc_exposure_mode(self, em, is_default=False):
        if not is_default :
            section = 'params-exposure'
        else:
            section = 'DEFAULT'

        if em == globals.AGC_EXPOSURE_MODE_NORMAL:
            self.parser[section]['agc_exposure_mode'] = 'normal'
        elif em == globals.AGC_EXPOSURE_MODE_SHORT:
            self.parser[section]['agc_exposure_mode'] = 'short'
        elif em == globals.AGC_EXPOSURE_MODE_LONG:
            self.parser[section]['agc_exposure_mode'] = 'long'
        elif em == globals.AGC_EXPOSURE_MODE_CUSTOM:
            self.parser[section]['agc_exposure_mode'] = 'custom'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_agc_exposure_compensation(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            ec = self.parser.getint('params-exposure', 'agc_exposure_compensation')
        else:
            ec = self.parser.getint('DEFAULT', 'agc_exposure_compensation')

        if -8.0 <= ec <= 8.0:
            return ec
        else:
            return 0

    def save_agc_exposure_compensation(self, ec, is_default=False):
        if not is_default :
            section = 'params-exposure'
        else:
            section = 'DEFAULT'

        if -8.0 <= ec <= 8.0:
            ec_string = str(ec)
            self.parser[section]['agc_exposure_compensation'] = ec_string

            # Configuration will be changed only when a new image will be captured and saved
            self.set_configuration_was_changed(update_configuration_file=False)

    def get_agc_metering_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            mm = self.parser['params-exposure']['agc_metering_mode']
        else:
            mm = self.parser['DEFAULT']['agc_metering_mode']

        if mm == 'center weighted':
            return globals.AGC_METERING_MODE_CENTER_WEIGHTED
        elif mm == 'spot':
            return globals.AGC_METERING_MODE_SPOT
        elif mm == 'matrix':
            return globals.AGC_METERING_MODE_MATRIX
        elif mm == 'custom':
            return globals.AGC_METERING_MODE_CUSTOM
        else:
            return globals.AGC_METERING_MODE_DEFAULT

    def save_agc_metering_mode(self, mm, is_default=False):
        if not is_default :
            section = 'params-exposure'
        else:
            section = 'DEFAULT'

        if mm == globals.AGC_METERING_MODE_CENTER_WEIGHTED:
            self.parser[section]['agc_metering_mode'] = 'center weighted'
        elif mm == globals.AGC_METERING_MODE_SPOT:
            self.parser[section]['agc_metering_mode'] = 'spot'
        elif mm == globals.AGC_METERING_MODE_MATRIX:
            self.parser[section]['agc_metering_mode'] = 'matrix'
        elif mm == globals.AGC_METERING_MODE_CUSTOM:
            self.parser[section]['agc_metering_mode'] = 'custom'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_exposure_time(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            return int(self.parser.getint('params-exposure', 'exposure_time'))
        else:
            return int(self.parser.getint('DEFAULT', 'exposure_time'))

    def save_exposure_time(self, et, is_default=False):
        if not is_default :
            section = 'params-exposure'
        else:
            section = 'DEFAULT'

        self.parser[section]['exposure_time'] = str(et)

        # Configuration will be changed only when a new image will be captured and saved
        self.set_configuration_was_changed(update_configuration_file=False)

    def get_analog_gain(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            return int(self.parser.getfloat('params-exposure', 'analog_gain'))
        else:
            return int(self.parser.getfloat('DEFAULT', 'analog_gain'))

    def save_analog_gain(self, ag, is_default=False):
        if not is_default :
            section = 'params-exposure'
        else:
            section = 'DEFAULT'

        self.parser[section]['analog_gain'] = str(ag)

        # Configuration will be changed only when a new image will be captured and saved
        self.set_configuration_was_changed(update_configuration_file=False)

    def get_auto_white_balance_enabled(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            awbe = self.parser['params-picture']['auto_white_balance_enabled']
        else:
            awbe = self.parser['DEFAULT']['auto_white_balance_enabled']

        if awbe == 'yes':
            return globals.AUTO_WHITE_BALANCE_ENABLED
        elif awbe == 'no':
            return globals.AUTO_WHITE_BALANCE_DISABLED
        else:
            return globals.AUTO_WHITE_BALANCE_EN_DIS_DEFAULT

    def save_auto_white_balance_enabled(self, wbe, is_default=False):
        if not is_default :
            section = 'params-picture'
        else:
            section = 'DEFAULT'

        if wbe == globals.AUTO_WHITE_BALANCE_ENABLED:
            self.parser[section]['auto_white_balance_enabled'] = 'yes'
        elif wbe == globals.AUTO_WHITE_BALANCE_DISABLED:
            self.parser[section]['auto_white_balance_enabled'] = 'no'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_auto_white_balance_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            awbm = self.parser['params-picture']['auto_white_balance_mode']
        else:
            awbm = self.parser['DEFAULT']['auto_white_balance_mode']

        if awbm == 'auto':
            return globals.WHITE_BALANCE_MODE_AUTO
        elif awbm == 'tungsten':
            return globals.WHITE_BALANCE_MODE_TUNGSTEN
        elif awbm == 'fluorescent':
            return globals.WHITE_BALANCE_MODE_FLUORESCENT
        elif awbm == 'indoor':
            return globals.WHITE_BALANCE_MODE_INDOOR
        elif awbm == 'daylight':
            return globals.WHITE_BALANCE_MODE_DAYLIGHT
        elif awbm == 'cloudy':
            return globals.WHITE_BALANCE_MODE_CLOUDY
        elif awbm == 'custom':
            return globals.WHITE_BALANCE_MODE_CUSTOM
        else:
            return globals.WHITE_BALANCE_MODE_DEFAULT

    def save_auto_white_balance_mode(self, awbm, is_default=False):
        if not is_default :
            section = 'params-picture'
        else:
            section = 'DEFAULT'

        if awbm == globals.WHITE_BALANCE_MODE_AUTO:
            self.parser[section]['auto_white_balance_mode'] = 'auto'
        elif awbm == globals.WHITE_BALANCE_MODE_TUNGSTEN:
            self.parser[section]['auto_white_balance_mode'] = 'tungsten'
        elif awbm == globals.WHITE_BALANCE_MODE_FLUORESCENT:
            self.parser[section]['auto_white_balance_mode'] = 'fluorescent'
        elif awbm == globals.WHITE_BALANCE_MODE_INDOOR:
            self.parser[section]['auto_white_balance_mode'] = 'indoor'
        elif awbm == globals.WHITE_BALANCE_MODE_DAYLIGHT:
            self.parser[section]['auto_white_balance_mode'] = 'daylight'
        elif awbm == globals.WHITE_BALANCE_MODE_CLOUDY:
            self.parser[section]['auto_white_balance_mode'] = 'cloudy'
        elif awbm == globals.WHITE_BALANCE_MODE_CUSTOM:
            self.parser[section]['auto_white_balance_mode'] = 'custom'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_color_saturation(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            return int(self.parser['params-picture']['color_saturation'])
        else:
            return int(self.parser['DEFAULT']['color_saturation'])

    def save_color_saturation(self, cs, is_default=False):
        if not is_default :
            section = 'params-picture'
        else:
            section = 'DEFAULT'

        self.parser[section]['color_saturation'] = str(cs)

        # Configuration will be changed only when a new image will be captured and saved
        self.set_configuration_was_changed(update_configuration_file=False)

    def get_sharpness_level(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            return int(self.parser['params-picture']['sharpness_level'])
        else:
            return int(self.parser['DEFAULT']['sharpness_level'])

    def save_sharpness_level(self, sl, is_default=False):
        if not is_default :
            section = 'params-picture'
        else:
            section = 'DEFAULT'

        self.parser['DEFAULT']['sharpness_level'] = str(sl)

        # Configuration will be changed only when a new image will be captured and saved
        self.set_configuration_was_changed(update_configuration_file=False)

    def get_noise_reduction_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            nrm = self.parser['params-picture']['noise_reduction_mode']
        else:
            nrm = self.parser['DEFAULT']['noise_reduction_mode']

        if nrm == 'off':
            return globals.NOISE_REDUCTION_MODE_OFF
        elif nrm == 'fast':
            return globals.NOISE_REDUCTION_MODE_FAST
        elif nrm == 'high_quality':
            return globals.NOISE_REDUCTION_MODE_HIGH_QUALITY
        else:
            return globals.NOISE_REDUCTION_MODE_DEFAULT

    def save_noise_reduction_mode(self, nrm, is_default=False):
        if not is_default :
            section = 'params-picture'
        else:
            section = 'DEFAULT'

        if nrm == globals.NOISE_REDUCTION_MODE_OFF:
            self.parser[section]['noise_reduction_mode'] = 'off'
        elif nrm == globals.NOISE_REDUCTION_MODE_FAST:
            self.parser[section]['noise_reduction_mode'] = 'fast'
        if nrm == globals.NOISE_REDUCTION_MODE_HIGH_QUALITY:
            self.parser[section]['noise_reduction_mode'] = 'high_quality'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_contrast_level(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            return int(self.parser['params-picture']['contrast_level'])
        else:
            return int(self.parser['DEFAULT']['contrast_level'])

    def save_contrast_level(self, cl, is_default=False):
        if not is_default :
            section = 'params-picture'
        else:
            section = 'DEFAULT'

        self.parser[section]['contrast_level'] = str(cl)

        # Configuration will be changed only when a new image will be captured and saved
        self.set_configuration_was_changed(update_configuration_file=False)

    def get_brightness_level(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            return int(self.parser['params-picture']['brightness_level'])
        else:
            return int(self.parser['DEFAULT']['brightness_level'])

    def save_brightness_level(self, bl, is_default=False):
        if not is_default :
            section = 'params-picture'
        else:
            section = 'DEFAULT'

        self.parser[section]['brightness_level'] = str(bl)

        # Configuration will be changed only when a new image will be captured and saved
        self.set_configuration_was_changed(update_configuration_file=False)

    def get_captured_image_quality(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            return int(self.parser['params-picture']['captured_image_quality'])
        else:
            return int(self.parser['DEFAULT']['captured_image_quality'])

    def save_captured_image_quality(self, ciq, is_default=False):
        if not is_default :
            section = 'params-picture'
        else:
            section = 'DEFAULT'

        self.parser[section]['captured_image_quality'] = str(ciq)

        # Configuration will be changed only when a new image will be captured and saved
        self.set_configuration_was_changed(update_configuration_file=False)

    def get_shoot_delay_timer_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            sdtm = self.parser['params-timers']['shoot_delay_timer_mode']
        else:
            sdtm = self.parser['DEFAULT']['shoot_delay_timer_mode']

        if sdtm == 'none':
            return globals.SHOOT_DELAY_NONE
        elif sdtm == '2 Sec':
            return globals.SHOOT_DELAY_2S
        elif sdtm == '5 Sec':
            return globals.SHOOT_DELAY_5S
        elif sdtm == '10 Sec':
            return globals.SHOOT_DELAY_10S
        elif sdtm == '15 Sec':
            return globals.SHOOT_DELAY_15S
        else:
            return globals.SHOOT_DELAY_DEFAULT

    def save_shoot_delay_timer_mode(self, sdtm, is_default=False):
        if not is_default :
            section = 'params-timers'
        else:
            section = 'DEFAULT'

        if sdtm == globals.SHOOT_DELAY_NONE:
            self.parser[section]['shoot_delay_timer_mode'] = 'none'
        elif sdtm == globals.SHOOT_DELAY_2S:
            self.parser[section]['shoot_delay_timer_mode'] = '2 Sec'
        elif sdtm == globals.SHOOT_DELAY_5S:
            self.parser[section]['shoot_delay_timer_mode'] = '5 Sec'
        elif sdtm == globals.SHOOT_DELAY_10S:
            self.parser[section]['shoot_delay_timer_mode'] = '10 Sec'
        elif sdtm == globals.SHOOT_DELAY_15S:
            self.parser[section]['shoot_delay_timer_mode'] = '15 Sec'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_shoot_delay_beeps_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            sdbn = self.parser['params-timers']['shoot_delay_beeps_mode']
        else:
            sdbn = self.parser['DEFAULT']['shoot_delay_beeps_mode']

        if sdbn == 'OFF':
            return globals.SHOOT_DELAY_BEEPS_OFF
        elif sdbn == 'Ongoing':
            return globals.SHOOT_DELAY_BEEPS_ONGOING
        elif sdbn == 'Start Stop':
            return globals.SHOOT_DELAY_BEEPS_START_STOP
        else:
            return globals.SHOOT_DELAY_BEEPS_DEFAULT

    def save_shoot_delay_beeps_mode(self, sdbn, is_default=False):
        if not is_default :
            section = 'params-timers'
        else:
            section = 'DEFAULT'

        if sdbn == globals.SHOOT_DELAY_BEEPS_OFF:
            self.parser[section]['shoot_delay_beeps_mode'] = 'OFF'
        elif sdbn == globals.SHOOT_DELAY_BEEPS_ONGOING:
            self.parser[section]['shoot_delay_beeps_mode'] = 'Ongoing'
        elif sdbn == globals.SHOOT_DELAY_BEEPS_START_STOP:
            self.parser[section]['shoot_delay_beeps_mode'] = 'Start Stop'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_on_screen_parameters_enabled(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            ospe = self.parser['params-display']['on_screen_parameters_enabled']
        else:
            ospe = self.parser['DEFAULT']['on_screen_parameters_enabled']

        if ospe == 'yes':
            return globals.ON_SCREEN_PARAMS_ENABLED
        elif ospe == 'no':
            return globals.ON_SCREEN_PARAMS_DISABLED
        else:
            return globals.ON_SCREEN_PARAMS_DEFAULT

    def save_on_screen_parameters_enabled(self, ospe, is_default=False):
        if not is_default :
            section = 'params-display'
        else:
            section = 'DEFAULT'

        if ospe == globals.ON_SCREEN_PARAMS_ENABLED:
            self.parser[section]['on_screen_parameters_enabled'] = 'yes'
        elif ospe == globals.ON_SCREEN_PARAMS_DISABLED:
            self.parser[section]['on_screen_parameters_enabled'] = 'no'

        self.set_configuration_was_changed(update_configuration_file=
                                           True)

    def get_live_settings_enabled(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            lse = self.parser['params-display']['live_settings_enabled']
        else:
            lse = self.parser['DEFAULT']['live_settings_enabled']

        if lse == 'yes':
            return globals.LIVE_SETTING_ENABLED
        elif lse == 'no':
            return globals.LIVE_SETTING_DISABLED
        else:
            return globals.LIVE_SETTING_DEFAULT

    def save_live_settings_enabled(self, lse, is_default=False):
        if not is_default :
            section = 'params-display'
        else:
            section = 'DEFAULT'

        if lse == globals.LIVE_SETTING_ENABLED:
            self.parser[section]['live_settings_enabled'] = 'yes'
        elif lse == globals.LIVE_SETTING_DISABLED:
            self.parser[section]['live_settings_enabled'] = 'no'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_focus_measure_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            fmm = self.parser['params-display']['focus_measure_mode']
        else:
            fmm = self.parser['DEFAULT']['focus_measure_mode']

        if fmm == 'none':
            return globals.FOCUS_MEASURE_MODE_NONE
        elif fmm == 'center 50x50':
            return globals.FOCUS_MEASURE_MODE_CENTER_50X50
        elif fmm == 'center 100x100':
            return globals.FOCUS_MEASURE_MODE_CENTER_100X100
        elif fmm == 'center 200x200':
            return globals.FOCUS_MEASURE_MODE_CENTER_200X200
        else:
            return globals.FOCUS_MEASURE_MODE_DEFAULT

    def save_focus_measure_mode(self, fmm, is_default=False):
        if not is_default :
            section = 'params-display'
        else:
            section = 'DEFAULT'

        if fmm == globals.FOCUS_MEASURE_MODE_NONE:
            self.parser[section]['focus_measure_mode'] = 'none'
        elif fmm == globals.FOCUS_MEASURE_MODE_CENTER_50X50:
            self.parser[section]['focus_measure_mode'] = 'center 50x50'
        elif fmm == globals.FOCUS_MEASURE_MODE_CENTER_100X100:
            self.parser[section]['focus_measure_mode'] = 'center 100x100'
        elif fmm == globals.FOCUS_MEASURE_MODE_CENTER_200X200:
            self.parser[section]['focus_measure_mode'] = 'center 200x200'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_preview_frame_rate(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            pfr = self.parser['params-display']['preview_frame_rate']
        else:
            pfr = self.parser['DEFAULT']['preview_frame_rate']

        if 'pfr' == '30':
            return globals.PREVIEW_FPS_30
        elif 'pfr' == '15':
            return globals.PREVIEW_FPS_15
        elif 'pfr' == '10':
            return globals.PREVIEW_FPS_10
        elif 'pfr' == 'stills':
            return globals.PREVIEW_FPS_STILLS
        else:
            return globals.PREVIEW_FPS_DEFAULT

    def save_preview_frame_rate(self, pfr, is_default=False):
        if not is_default :
            section = 'params-display'
        else:
            section = 'DEFAULT'

        if pfr == globals.PREVIEW_FPS_30:
            self.parser[section]['preview_frame_rate'] = '30'
        elif pfr == globals.PREVIEW_FPS_15:
            self.parser[section]['preview_frame_rate'] = '15'
        elif pfr == globals.PREVIEW_FPS_10:
            self.parser[section]['preview_frame_rate'] = '10'
        elif pfr == globals.PREVIEW_FPS_STILLS:
            self.parser[section]['preview_frame_rate'] = 'stills'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_show_histogram_enabled(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            she = self.parser['params-display']['show_histogram_enabled']
        else:
            she = self.parser['DEFAULT']['show_histogram_enabled']

        if she == 'no':
            return globals.HISTOGRAM_DISABLED
        elif she == 'yes':
            return globals.HISTOGRAM_ENABLED
        else:
            return globals.HISTOGRAM_DEFAULT

    def save_show_histogram_enabled(self, she, is_default=False):
        if not is_default :
            section = 'params-display'
        else:
            section = 'DEFAULT'

        if she == globals.HISTOGRAM_DISABLED:
            self.parser[section]['show_histogram_enabled'] = 'no'
        elif she == globals.HISTOGRAM_ENABLED:
            self.parser[section]['show_histogram_enabled'] = 'yes'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_display_transform_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            dtm = self.parser['params-display']['display_transform_mode']
        else:
            dtm = self.parser['DEFAULT']['display_transform_mode']

        if dtm == 'none':
            return globals.DISPLAY_TRANSFORM_NONE
        elif dtm == 'h flip horizontal mirror':
            return globals.DISPLAY_TRANSFORM_H_FLIP_HORIZONTAL_MIRROR
        elif dtm == 'v flip swap up down':
            return globals.DISPLAY_TRANSFORM_V_FLIP_SWAP_UP_DOWN
        elif dtm == 'h and v flip rotate 180':
            return globals.DISPLAY_TRANSFORM_H_AND_V_FLIP_ROTATE_180
        else:
            return globals.DISPLAY_TRANSFORM_DEFAULT

    def save_display_transform_mode(self, dtm, is_default=False):
        if not is_default :
            section = 'params-display'
        else:
            section = 'DEFAULT'

        if dtm == globals.DISPLAY_TRANSFORM_NONE:
            self.parser[section]['display_transform_mode'] = 'none'
        elif dtm == globals.DISPLAY_TRANSFORM_H_FLIP_HORIZONTAL_MIRROR:
            self.parser[section]['display_transform_mode'] = 'h flip horizontal mirror'
        elif dtm == globals.DISPLAY_TRANSFORM_V_FLIP_SWAP_UP_DOWN:
            self.parser[section]['display_transform_mode'] = 'v flip swap up down'
        elif dtm == globals.DISPLAY_TRANSFORM_H_AND_V_FLIP_ROTATE_180:
            self.parser[section]['display_transform_mode'] = 'h and v flip rotate 180'

        self.set_configuration_was_changed(update_configuration_file=False)

    def get_flash_mode(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            fm = self.parser['params-flash']['flash_mode']
        else:
            fm = self.parser['DEFAULT']['flash_mode']

        if fm == 'disabled':
            return globals.FLASH_MODE_DISABLE
        elif fm == 'front':
            return globals.FLASH_MODE_FRONT
        elif fm == 'back':
            return globals.FLASH_MODE_BACK
        else:
            return globals.FLASH_MODE_DEFAULT

    def save_flash_mode(self, fm, is_default=False):
        if not is_default :
            section = 'params-flash'
        else:
            section = 'DEFAULT'

        if fm == globals.FLASH_MODE_DISABLE:
            self.parser[section]['flash_mode'] = 'disabled'
        elif fm == globals.FLASH_MODE_FRONT:
            self.parser[section]['flash_mode'] = 'front'
        elif fm == globals.FLASH_MODE_BACK:
            self.parser[section]['flash_mode'] = 'back'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_flash_delay(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            fd = self.parser['params-flash']['flash_delay']
        else:
            fd = self.parser['DEFAULT']['flash_delay']

        if fd == 'none':
            return globals.FLASH_DELAY_NONE
        elif fd == '0.1 sec':
            return globals.FLASH_DELAY_0_1_SEC
        elif fd == '0.2 sec':
            return globals.FLASH_DELAY_0_2_SEC
        elif fd == '0.5 sec':
            return globals.FLASH_DELAY_0_5_SEC
        elif fd == '1 sec':
            return globals.FLASH_DELAY_1_SEC
        elif fd == '2 sec':
            return globals.FLASH_DELAY_2_SEC
        elif fd == '5 sec':
            return globals.FLASH_DELAY_5_SEC
        else:
            return globals.FLASH_DELAY_DEFAULT

    def save_flash_delay(self, fd, is_default=False):
        if not is_default :
            section = 'params-flash'
        else:
            section = 'DEFAULT'

        if fd == globals.FLASH_DELAY_NONE:
            self.parser[section]['flash_delay'] = 'none'
        elif fd == globals.FLASH_DELAY_0_1_SEC:
            self.parser[section]['flash_delay'] = '0.1 sec'
        elif fd == globals.FLASH_DELAY_0_2_SEC:
            self.parser[section]['flash_delay'] = '0.2 sec'
        elif fd == globals.FLASH_DELAY_0_5_SEC:
            self.parser[section]['flash_delay'] = '0.5 sec'
        elif fd == globals.FLASH_DELAY_1_SEC:
            self.parser[section]['flash_delay'] = '1 sec'
        elif fd == globals.FLASH_DELAY_2_SEC:
            self.parser[section]['flash_delay'] = '2 sec'
        elif fd == globals.FLASH_DELAY_5_SEC:
            self.parser[section]['flash_delay'] = '5 sec'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_power_save_timeout(self):
        if self.powerup_configuration_mode == globals.POWER_UP_CONFIGURATION_LAST:
            pst = self.parser['system']['power_save_timeout']
        else:
            pst = self.parser['DEFAULT']['power_save_timeout']

        if pst == '1 minute':
            return globals.POWER_SAVE_TIMER_MODE_1_MIN
        elif pst == '2 minutes':
            return globals.POWER_SAVE_TIMER_MODE_2_MIN
        elif pst == '5 minutes':
            return globals.POWER_SAVE_TIMER_MODE_5_MIN
        elif pst == '10 minutes':
            return globals.POWER_SAVE_TIMER_MODE_10_MIN
        elif pst == 'disabled':
            return globals.POWER_SAVE_TIMER_MODE_DISABLED
        else:
            return globals.POWER_SAVE_TIMER_MODE_DEFAULT

    def save_power_save_timeout(self, pst, is_default=False):
        if not is_default:
            section = 'system'
        else:
            section = 'DEFAULT'

        if pst == globals.POWER_SAVE_TIMER_MODE_1_MIN:
            self.parser[section]['power_save_timeout'] = '1 minute'
        elif pst == globals.POWER_SAVE_TIMER_MODE_2_MIN:
            self.parser[section]['power_save_timeout'] = '2 minutes'
        elif pst == globals.POWER_SAVE_TIMER_MODE_5_MIN:
            self.parser[section]['power_save_timeout'] = '5 minutes'
        elif pst == globals.POWER_SAVE_TIMER_MODE_10_MIN:
            self.parser[section]['power_save_timeout'] = '10 minutes'
        elif pst == globals.POWER_SAVE_TIMER_MODE_DISABLED:
            self.parser[section]['power_save_timeout'] = 'disabled'

        self.set_configuration_was_changed(update_configuration_file=True)

    def get_last_image_file_index(self):
        self.parser.read(self.configuration_file_name)
        self.last_image_file_index = self.parser.get('image_files', 'last_image_files_last_index')
        return self.last_image_file_index

    def get_max_image_index(self):
        self.parser.read(self.configuration_file_name)
        self.max_image_file_index = self.parser.get('image_files', 'max_image_files_index')
        return self.max_image_file_index

    def get_next_image_file_index(self):
        """ This function gets the last image index from the configuration ini file and increment it by 1.
            The image index value is set to 0 if the index value exceeds the maximum index value.
            The function writes the new value back to the configuration ini file.
            The function returns the new value.
        """
        self.get_last_image_file_index()
        self.get_max_image_index()
        self.last_image_file_index = str(int(self.last_image_file_index) + 1)
        if int(self.last_image_file_index) > int(self.max_image_file_index):
            self.last_image_file_index = '0'
        self.parser['image_files']['last_image_files_last_index'] = self.last_image_file_index
        # with open(self.configuration_file_name, 'w') as config_file:
        #  self.parser.write(config_file)
        self.save_configuration()

        return self.last_image_file_index


if __name__ == "__main__":
    while True:
        configuration = ConfigurationManager()

        # print(configuration.get_last_image_file_index(), "  ", configuration.get_next_image_file_index())
        # print(configuration.parser.sections())
        # print(configuration.parser["params-exposure"].getfloat('analog_gain'))
        print(configuration.get_exposure_mode())

        time.sleep(1)
