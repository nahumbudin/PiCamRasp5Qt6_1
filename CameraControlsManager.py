from libcamera import controls, Transform
from picamera2.controls import Controls
import globals
from FlashControl import FlashControl


class CameraControlsManager:
    """ This class manages the camera controls handling """

    def __init__(self, preview_configuration, capture_configuration, camera):
        self.camera = None
        self.message_prefix = None
        self.message_param = None
        self.preview_configuration = preview_configuration
        self.capture_config = capture_configuration
        self.camera = camera

        self.shoot_delay_mode = 0  # No delay
        self.shoot_delay_beeps_mode = 0  # No beeps.
        self.exposure_beeps_mode = 0  # No beeps

        self.still_exposure_time = 30000

        self.flash_control = FlashControl(self.camera)

    def get_shoot_delay_mode(self):
        return self.shoot_delay_mode

    def get_shoot_delay_beeps_mode(self):
        return self.shoot_delay_beeps_mode

    def get_exposure_beeps_mode(self):
        return self.exposure_beeps_mode

    def get_still_exposure_time(self):
        return self.still_exposure_time

    def set_preview_fps(self, fps):
        self.camera.stop()
        self.preview_configuration.controls.FrameRate = fps
        self.camera.configure("preview")
        self.camera.start()

    def parse_messages(self, mssg, cam):

        self.camera = cam
        self.message_prefix = mssg[:10]
        self.message_param = mssg[10:]

        if self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_AGC_MODE[:10]:
            agc_mode = self.message_param[2:] == '0'  # enabled (True) if index 0 is selected

            ctrls = Controls(self.camera)
            ctrls.AeEnable = agc_mode
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.AeEnable = agc_mode

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_AGC_CONSTRAINT_MODE[:10]:
            constraint_mode = globals.auto_exposure_constraints_modes[self.message_param]

            ctrls = Controls(self.camera)
            ctrls.AeConstraintMode = constraint_mode
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.AeConstraintMode = constraint_mode

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_AGC_EXPOSURE_MODE[:10]:
            exposure_mode = globals.auto_exposure_constraints_modes[self.message_param]

            ctrls = Controls(self.camera)
            ctrls.AeExposureMode = exposure_mode
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.AeExposureMode = exposure_mode

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_EXPOSURE_TIME[:10]:
            self.still_exposure_time = globals.exposure_time_values[self.message_param]

            ctrls = Controls(self.camera)
            ctrls.ExposureTime = self.still_exposure_time
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.ExposureTime = self.still_exposure_time

            if self.still_exposure_time > 33333:
                # lower than 30fps is required
                # ctrls = Controls(camera)
                # ctrls.FrameDurationLimits = (exposure_time, exposure_time)
                # camera.set_controls(ctrls)
                self.camera.still_configuration.controls.FrameDurationLimits = (
                    self.still_exposure_time, self.still_exposure_time)

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_GAIN[:10]:
            gain = float(self.message_param) / 10

            ctrls = Controls(self.camera)
            ctrls.AnalogueGain = gain
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.AnalogueGain = gain

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_EXPOSURE_COMPENSATION[:10]:
            exposure_comp = float(self.message_param)

            ctrls = Controls(self.camera)
            ctrls.ExposureValue = exposure_comp
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.ExposureValue = exposure_comp

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_AGC_METERING_MODE[:10]:
            metering_mode = globals.auto_exposure_metering_mode[self.message_param]

            ctrls = Controls(self.camera)
            ctrls.AeMeteringMode = metering_mode
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.AeMeteringMode = metering_mode

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_AWB_ENABLE[:10]:

            awb_enable = self.message_param[2:] == '0'  # enabled (True) if index 0 is selected

            ctrls = Controls(self.camera)
            ctrls.AwbEnable = awb_enable
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.AwbEnable = awb_enable

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_WB_MODE[:10]:
            white_balance_mode = globals.white_balance_modes[self.message_param]

            ctrls = Controls(self.camera)
            ctrls.AwbMode = white_balance_mode
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.AwbMode = white_balance_mode

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_SATURATION[:10]:
            saturation_string = self.message_param[:2] + '.' + self.message_param[2:]
            saturation = float(saturation_string)

            ctrls = Controls(self.camera)
            ctrls.Saturation = saturation
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.Saturation = saturation

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_SHARPNESS[:10]:
            sharpness_string = self.message_param[:2] + '.' + self.message_param[2:]
            sharpness = float(sharpness_string)

            print("Sharpness", sharpness)

            ctrls = Controls(self.camera)
            ctrls.Sharpness = sharpness
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.Sharpness = sharpness

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_NOISE_REDUCTION_MODE[:10]:
            noise_reduction_mode = globals.noise_reduction_modes[self.message_param]

            ctrls = Controls(self.camera)
            ctrls.NoiseReductionMode = noise_reduction_mode
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.NoiseReductionMode = noise_reduction_mode

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_CONTRAST[:10]:
            contrast_string = self.message_param[:2] + '.' + self.message_param[2:]
            contrast = float(contrast_string)

            ctrls = Controls(self.camera)
            ctrls.Contrast = contrast
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.Contrast = contrast

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_BRIGHTNESS[:10]:
            brightness_string = self.message_param[:1] + '.' + self.message_param[1:]
            brightness = float(brightness_string)

            ctrls = Controls(self.camera)
            ctrls.Brightness = brightness
            self.camera.set_controls(ctrls)

            self.camera.still_configuration.controls.Brightness = brightness

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_QUALITY[:10]:
            quality = int(self.message_param)
            self.camera.options["quality"] = quality

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_SHOOT_DELAY[:10]:
            shoot_delay_mode_string = self.message_param[2:]
            self.shoot_delay_mode = int(shoot_delay_mode_string)

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_SHOOT_DELAY_BEEPS[:10]:
            shoot_delay_beeps_mode_string = self.message_param[2:]
            self.shoot_delay_beeps_mode = int(shoot_delay_beeps_mode_string)

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_EXPOSURE_BEEPS[:10]:
            exposure_beeps_mode_string = self.message_param[2:]
            self.exposure_beeps_mode = int(exposure_beeps_mode_string)

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_FLASH_MODE[:10]:
            flash_mode_string = self.message_param[2:]
            self.flash_control.set_flash_mode(int(flash_mode_string))

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_FLASH_DELAY[:10]:
            flash_delay_string = self.message_param[2:]
            self.flash_control.set_flash_delay(int(flash_delay_string))

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_PREVIEW_FPS[:10]:
            if self.message_param == "000":
                self.set_preview_fps(30)
            elif self.message_param == "001":
                self.set_preview_fps(15)
            elif self.message_param == "002":
                self.set_preview_fps(10)
            elif self.message_param == "003":  # Temp; Stills
                # self.set_preview_fps(5)
                pass
            elif self.message_param == "004":
                #  self.set_preview_fps(1)
                pass
            elif self.message_param == "005":
                pass

        elif self.message_prefix == globals.DEFAULT_CAMERA_CONTROL_PIC_TRANSFORM[:10]:
            if self.message_param == "000":
                self.camera.preview_configuration.transform = Transform()
                self.capture_config["transform"] = Transform()
            elif self.message_param == "001":
                self.camera.preview_configuration.transform = Transform(hflip=True)
                self.capture_config["transform"] = Transform(hflip=True)
            elif self.message_param == "002":
                self.camera.preview_configuration.transform = Transform(vflip=True)
                self.capture_config["transform"] = Transform(vflip=True)
            elif self.message_param == "003":
                self.camera.preview_configuration.transform = Transform(hflip=True, vflip=True)
                self.capture_config["transform"] = Transform(hflip=True, vflip=True)

            self.camera.stop()
            self.camera.configure("preview")
            self.camera.start()
