from multiprocessing import Event
import time
import threading
# from PiCamIO import PiCamIOhandler
from Raspi5IO import Raspi5IO


def shooting_thread(exit_event,
                    ext_pressed_callback_func=None,
                    ext_released_callback_func=None,
                    ext_press_event=None,
                    ext_release_event=None):
    """ This thread handles the shooting switch events.
        The parameters are callback functions and events that
        will be initiated when the shoot switch is pressed or released. """

    def pressed_callback_func(channel):
        # pi_cam_io.activate_flash(50, 2000)
        ext_pressed_callback_func(channel)

    def released_callback_func(channel):
        ext_released_callback_func(channel)

    ext_event = exit_event

    pi_cam_io = Raspi5IO(pressed_callback_func=pressed_callback_func,
                         released_callback_func=released_callback_func,
                         pressed_event=ext_press_event,
                         released_event=ext_release_event,
                         thread_exit_event=exit_event)

    thread_running = True

    # shoot_switch_level = pi_cam_io.read_shoot_switch()

    # prev_shoot_switch_level = not shoot_switch_level
    # shoot_switch_state = pi_cam_io.SWITCH_STATE_RELEASED

    # if not shoot_switch_level:
    #     shoot_switch_state = pi_cam_io.SWITCH_STATE_PRESSED

    print("shoot thread is running")

    while thread_running:
        """ Wait for a change in the shooting switch state. """

        """ Handled by the switch IO callbacks """

        """
        shoot_switch_level = pi_cam_io.read_shoot_switch()
        if shoot_switch_level == prev_shoot_switch_level:
            # a stable switch state
            if shoot_switch_state == pi_cam_io.SWITCH_STATE_RELEASED:
                if not shoot_switch_level:
                    # switch state was changed from released to pressed
                    shoot_switch_state = pi_cam_io.SWITCH_STATE_PRESSED
                    pressed_callback_func(0)
            else:
                # switch is pressed:
                if shoot_switch_level:
                    # switch state was changed from pressed to released
                    shoot_switch_state = pi_cam_io.SWITCH_STATE_RELEASED
                    released_callback_func(0)

        prev_shoot_switch_level = shoot_switch_level
        """

        if ext_event.is_set():
            thread_running = False
            print("Shooting thread exiting...")

        time.sleep(pi_cam_io.DEBOUNCE_TIME_MS / 1000)


if __name__ == '__main__':

    exit_thread_event = Event()


    def pressed_callback(channel):
        """ Called when the shooting switch is pressed. """
        # if flash_curtain_type == FRONT_FLASH:
        #   PiCamIO.activate_fash(10, 500)
        print("Thread Switch pressed")


    def released_callback(channel):
        """ Called when the shooting switch is released. """
        # if flash_curtain_type == BACK_FLASH:
        #    PiCamIO.activate_fash(10, 0)
        print("Thread Switch released")


    s_thread = threading.Thread(target=shooting_thread, daemon=True,
                                args=(exit_thread_event,
                                      pressed_callback,
                                      released_callback,
                                      None,
                                      None))
    s_thread.start()

    while True:
        #        print("main")
        time.sleep(1.0)
