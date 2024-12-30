class FlashControl:

    def __init__(self, camera):
        self.FLASH_MODE_OFF = 0
        self.FLASH_MODE_FRONT = 1
        self.FLASH_MODE_BACK = 2

        self.FLASH_DELAY_NONE = 0
        self.FLASH_DELAY_01_SEC = 0
        self.FLASH_DELAY_02_SEC = 0
        self.FLASH_DELAY_05_SEC = 0
        self.FLASH_DELAY_1_SEC = 0
        self.FLASH_DELAY_2_SEC = 0
        self.FLASH_DELAY_5_SEC = 0

        self.flash_mode = self.FLASH_MODE_OFF
        self.flash_delay = self.FLASH_DELAY_NONE
        self.camera_exposure_time = 0

        self.camera = camera

    def set_flash_mode(self, mode):
        if mode in range(self.FLASH_MODE_OFF, self.FLASH_MODE_BACK + 1):
            self.flash_mode = mode

    def get_flash_mode(self):
        return self.flash_mode

    def set_flash_delay(self, delay):
        if delay in range(self.FLASH_DELAY_NONE, self.FLASH_DELAY_5_SEC + 1):
            self.flash_delay = delay

    def get_flash_delay(self):
        return self.flash_delay

    def _set_camera_exposure_time(self, ext):
        self.camera_exposure_time = ext

    def query_camera_exposure_time(self):
        # exposure_time =
        pass

    def get_camera_exposure_time(self):
        return self.camera_exposure_time
