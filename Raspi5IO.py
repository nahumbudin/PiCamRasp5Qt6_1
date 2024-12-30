import threading
import time

import gpiod


class Raspi5IO:
    """
    This lass handles the Pi Camera IO pin:
        1. GPIO 25  : input  Shooting Switch (active low).
        2. GPIO 12  : output Flash Activation (active high).
        3. GPIO 7   : output Buzzer (active high)
        4. GPIO 24  : output Power Switch LED (active high)

        Author: Nahum Budin
        Date: 2024-02-03
        Version: 1.0.0
    """
    # IO pins
    GPIO_SWITCH_IN_PIN = 25 # pin 22
    GPIO_FLASH_OUT_PIN = 12  # pin 32
    GPIO_BUZZER_OUT_PIN = 7  # pin 26
    GPIO_LED_OUT_PIN = 24    # pin 18

    DEBOUNCE_TIME_MS = 10
    SWITCH_CHANGES_PER_SEC = 20  # High level debouncing
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
                 released_event=None,
                 thread_exit_event=None):
        """ Creates an IO handler  to handle the Shoot-Switch input and
        the Flash-fire output. The parameters are callback functions and events that
        will be initiated when the shoot switch is pressed or released. """
        # Use BCM channels  numbers
        # GPIO.cleanup((self.GPIO_SWITCH_IN_PIN, self.GPIO_FLASH_OUT_PIN))
        self.pressed_callback_function = pressed_callback_func
        self.released_callback_function = released_callback_func
        self.pressed_event = pressed_event
        self.released_event = released_event
        self.thread_exit_event = thread_exit_event

        self.switch_state = self.SWITCH_STATE_RELEASED
        self.switch_last_change_time = time.time_ns()

        # Map the GPIO
        self.chip = gpiod.Chip('gpiochip4')

        self.switch_in_io = self.chip.get_line(self.GPIO_SWITCH_IN_PIN)
        self.flash_out_io = self.chip.get_line(self.GPIO_FLASH_OUT_PIN)
        self.buzzer_out_io = self.chip.get_line(self.GPIO_BUZZER_OUT_PIN)
        self.led_out_io = self.chip.get_line(self.GPIO_LED_OUT_PIN)

        self.switch_in_io.request(consumer="SWITCH", type=gpiod.LINE_REQ_DIR_IN, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
        self.flash_out_io.request(consumer="FLASH", type=gpiod.LINE_REQ_DIR_OUT)
        self.buzzer_out_io.request(consumer="BUZZER", type=gpiod.LINE_REQ_DIR_OUT)
        self.led_out_io.request(consumer="LED", type=gpiod.LINE_REQ_DIR_OUT)

        # Start the shooting switch thread
        self.s_thread = threading.Thread(target=self.shoot_switch_event_thread,
                                         daemon=True,
                                         args=(self.thread_exit_event, 0))
        self.s_thread.start()

    def read_shoot_switch(self):
        """ Returns the shoot-switch input state. """
        input_sw = self.switch_in_io.get_value()
        return input_sw

    def query_switch_change_event(self):
        """ An event that is generated asynchronously (in a thread) when the shoot switch changes its state.
            Implements a debouncing state machine that limits the number of changes per second
            to SWITCH_CHANGES_PER_SEC .
            Calls a press or a release callback function pressed_callback_function()
            or released_callback_function()."""

        if time.time_ns() > self.switch_last_change_time + self.SWITCH_CHANGE_TIME_NS:
            # Limit bouncing by number of changes per second
            if self.switch_state == self.SWITCH_STATE_RELEASED:
                if not self.read_shoot_switch():
                    # Input is low: Switch is pressed
                    self.switch_state = self.SWITCH_STATE_PRESSED
                    self.switch_last_change_time = time.time_ns()
                    if self.pressed_callback_function:
                        self.pressed_callback_function(0)
                    if self.pressed_event:
                        self.pressed_event.set()
            elif self.switch_state == self.SWITCH_STATE_PRESSED:
                if self.read_shoot_switch():
                    # Input is high: Switch is released
                    self.switch_state = self.SWITCH_STATE_RELEASED
                    self.switch_last_change_time = time.time_ns()
                    if self.released_callback_function:
                        self.released_callback_function(0)
                    if self.released_event:
                        self.released_event.set()

    def set_flash_output_state(self, fstate):
        if fstate in range(0, 2):
            self.flash_out_io.set_value(fstate)

    def set_buzzer_output_state(self, bstate):
        if bstate in range(0, 2):
            self.buzzer_out_io.set_value(bstate)

    def set_power_switch_led_output_state(self, lstate):
        if lstate in range(0, 2):
            self.led_out_io.set_value(lstate)

    def shoot_switch_event_thread(self, thread_exit_event, dummy=0):
        """ This thread handles the shooting switch events.
            The parameters are callback functions and events that
            will be initiated when the shoot switch is pressed or released. """
        shoot_thread_is_running = True

        while shoot_thread_is_running:

            self.query_switch_change_event()

            if thread_exit_event.is_set():
                thread_running = False
                print("Shooting switch thread exiting...")

            time.sleep(self.DEBOUNCE_TIME_MS / 1000)

        self.set_power_switch_led_output_state(False)
        self.set_buzzer_output_state(False)


if __name__ == '__main__':
    from multiprocessing import Event

    exit_event = Event()
    press_event = Event()
    release_event = Event()

    buzzer_state = False
    led_state = False

    switch_count = 0
    led_count = 0

    def pressed_callback(channel):
        print("Switch pressed")

    def released_callback(channel):
        print("Switch released")

    pi5io = Raspi5IO(thread_exit_event=exit_event,
                     pressed_callback_func=pressed_callback,
                     released_callback_func=released_callback,
                     pressed_event=press_event,
                     released_event=release_event)

    while True:
        if press_event.is_set():
            print("Press Event", switch_count)
            press_event.clear()

        if release_event.is_set():
            print("Release Event", switch_count)
            release_event.clear()
            switch_count += 1

        led_count += 1
        if led_count >= 5:
            led_count = 0
            led_state = not led_state
            buzzer_state = not buzzer_state
            pi5io.set_flash_output_state(1)
            time.sleep(0.05)
            pi5io.set_flash_output_state(0)

        pi5io.set_power_switch_led_output_state(led_state)

        # pi5io.set_flash_output_state(led_state)

        # pi5io.set_buzzer_output_state(bstate=buzzer_state)
        #  buzzer_state = not buzzer_state

        time.sleep(0.1)

                                            