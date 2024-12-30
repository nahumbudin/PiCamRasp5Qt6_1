import RPi.GPIO as GPIO
import time
from multiprocessing import Event


class PiCamIOhandler():
    """
    This lass handles the Pi Camera IO pin:
        1. GPIO 16 : input  Shooting Switch (active low).
        2. GPIO 26 : output Flash Activation (active high).

         Author: Nahum Budin
        Date: 2023-09-24
        Version: 1.0.0
    """

    # IO pins
    GPIO_SWITCH_IN_PIN = 19  # pin 35(WHT)
    GPIO_FLASH_OUT_PIN = 13  # pin 33 (GRY)
    # (+3.3V = pin 1 (PRP); GND = pin 6 (BLK))

    DEBOUNCE_TIME_MS = 50
    SWITCH_CHANGES_PER_SEC = 100  # High level debouncing
    SWITCH_CHANGE_TIME_NS = 1000000000 / SWITCH_CHANGES_PER_SEC

    SWITCH_STATE_RELEASED = 0
    SWITCH_STATE_PRESSED = 1

    FLASH_MIN_ACTIVATION_TIME_MS = 10
    FLASH_MAX_ACTIVATION_TIME_MS = 100
    FLASH_MAX_LAG_TIME_MSEC = 2000
    flash_time_ms = FLASH_MIN_ACTIVATION_TIME_MS
    flash_lag_time_ms = 0
    flash_active = False

    def __init__(self, pressed_callback_func=None,
                 released_callback_func=None,
                 pressed_event=None,
                 release_event=None):
        """ Creates an IO handler  to handle the Shoot-Switch input and
        the Flash-fire output. The parameters are callback functions and events that
        will be initiated when the shoot switch is pressed or released. """
        # Use BCM channels  numbers
        # GPIO.cleanup((self.GPIO_SWITCH_IN_PIN, self.GPIO_FLASH_OUT_PIN))
        self.pressed_callback_function = pressed_callback_func
        self.release_callback_function = released_callback_func
        self.pressed_event = pressed_event
        self.released_event = release_event

        self.switch_state = self.SWITCH_STATE_RELEASED
        self.switch_last_change_time = time.time_ns()
        """
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(self.GPIO_SWITCH_IN_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.GPIO_FLASH_OUT_PIN, GPIO.OUT)
        GPIO.output(self.GPIO_FLASH_OUT_PIN, GPIO.LOW)

        GPIO.add_event_detect(self.GPIO_SWITCH_IN_PIN,
                              GPIO.BOTH,
                              callback=self.switch_change_event,
                              bouncetime=self.DEBOUNCE_TIME_MS)
        # GPIO.add_event_detect(self.GPIO_SWITCH_IN_PIN, GPIO.RISING, callback=self.switch_released_event)
        """

    def read_shoot_switch(self):
        """ Returns the shoot-switch input state. """
        input_sw = GPIO.input(self.GPIO_SWITCH_IN_PIN)
        return input_sw

    def switch_change_event(self, channel):
        """ An event that is generated asynchronously when the shoot switch changes its state.
            Implements a debouncing state machine that limits the number of changes per second
            to SWITCH_CHANGES_PER_SEC .
            Calls a press or a release callback function pressed_callback_function(channel)
            or released_callback_function(channel)."""

        if time.time_ns() > self.switch_last_change_time + self.SWITCH_CHANGE_TIME_NS:
            # Limit bouncing by number of changes per second
            if self.switch_state == self.SWITCH_STATE_RELEASED:
                if not self.read_shoot_switch():
                    # Input is low: Switch is pressed
                    self.switch_state = self.SWITCH_STATE_PRESSED
                    self.switch_last_change_time = time.time_ns()
                    if self.pressed_callback_function:
                        self.pressed_callback_function(channel)
                    if self.pressed_event:
                        self.pressed_event.set()
            elif self.switch_state == self.SWITCH_STATE_PRESSED:
                # Input is high: Switch is released
                self.switch_state = self.SWITCH_STATE_RELEASED
                self.switch_last_change_time = time.time_ns()
                if self.release_callback_function:
                    self.release_callback_function(channel)
                if self.released_event:
                    self.released_event.set()

    def activate_flash(self, active_time=FLASH_MIN_ACTIVATION_TIME_MS, delay=0):
        """     Activates the flash by setting high the flash activating IO pin for a duration
                of active_time in msec, after a time delay of delay msec, and then putting
                it goes back to low. """
        self.flash_time_ms = active_time
        if self.flash_time_ms < self.FLASH_MIN_ACTIVATION_TIME_MS:
            self.flash_time_ms = self.FLASH_MIN_ACTIVATION_TIME_MS
        elif self.flash_time_ms > self.FLASH_MAX_ACTIVATION_TIME_MS:
            self.flash_time_ms = self.FLASH_MAX_ACTIVATION_TIME_MS

        self.flash_lag_time_ms = delay
        if self.flash_lag_time_ms > self.FLASH_MAX_LAG_TIME_MSEC:
            self.flash_lag_time_ms = self.FLASH_MAX_LAG_TIME_MSEC

        if self.flash_lag_time_ms > 10:
            time.sleep(self.flash_lag_time_ms / 1000)

        if not self.flash_active:
            # Avoid double flash firing
            GPIO.output(self.GPIO_FLASH_OUT_PIN, GPIO.HIGH)
            self.flash_active = True
            time.sleep(self.flash_time_ms / 1000)
            GPIO.output(self.GPIO_FLASH_OUT_PIN, GPIO.LOW)
            self.flash_active = False


if __name__ == '__main__':
    """ Unittest. """
    FRONT_FLASH = 1
    BACK_FLASH = 0

    press_event = Event()
    release_event = Event()

    flash_curtain_type = FRONT_FLASH

    def pressed_callback(channel):
        print("Switch pressed")
        if flash_curtain_type == FRONT_FLASH:
            PiCamIO.activate_fash(10, 100)


    def released_callback(channel):
        print("Switch released")
        if flash_curtain_type == BACK_FLASH:
            PiCamIO.activate_fash(10, 0)


    PiCamIO = PiCamIOhandler(pressed_callback_func=None,
                             released_callback_func=released_callback,
                             pressed_event=press_event,
                             release_event=release_event)

    while True:
        if press_event.is_set():
            print("Press Event")
            press_event.clear()

        if release_event.is_set():
            print("Release Event")
            release_event.clear()

        time.sleep(0.01)
        # i = PiCamIO.read_shoot_switch()
        # print(i)
