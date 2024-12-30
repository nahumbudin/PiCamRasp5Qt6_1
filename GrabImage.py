import threading
import time

import BeepsPatternThread
import globals


def grab_image(cam_controls, bat_mon):
    """ Called when the shooting switch is pressed and grabs a hugh resolution image from the camera. """
    print("Grab image callback", time.time())
    camera_controls = cam_controls
    batx728 = bat_mon

    beeps_pattern = None

    shoot_delay_mode = camera_controls.get_shoot_delay_mode()
    shoot_delay_beeps_mode = camera_controls.get_shoot_delay_beeps_mode()

    if not shoot_delay_mode == 0:
        # Shoot delay is enabled
        if shoot_delay_beeps_mode == 0:
            # No beeps
            pass

        if shoot_delay_beeps_mode == 1:
            # Ongoing beeps
            if shoot_delay_mode == 1:
                beeps_pattern = globals.BEEPS_ONGOING_SEQUENCE_DELAY_2_SEC
            elif shoot_delay_mode == 2:
                beeps_pattern = globals.BEEPS_ONGOING_SEQUENCE_DELAY_5_SEC
            elif shoot_delay_mode == 3:
                beeps_pattern = globals.BEEPS_ONGOING_SEQUENCE_DELAY_10_SEC
            elif shoot_delay_mode == 4:
                beeps_pattern = globals.BEEPS_ONGOING_SEQUENCE_DELAY_15_SEC

        elif shoot_delay_beeps_mode == 2:
            # Start stop beeps
            if shoot_delay_mode == 1:
                beeps_pattern = globals.BEEPS_START_STOP_SEQUENCE_DELAY_2_SEC
            elif shoot_delay_mode == 2:
                beeps_pattern = globals.BEEPS_START_STOP_SEQUENCE_DELAY_5_SEC
            elif shoot_delay_mode == 3:
                beeps_pattern = globals.BEEPS_START_STOP_SEQUENCE_DELAY_10_SEC
            elif shoot_delay_mode == 4:
                beeps_pattern = globals.BEEPS_START_STOP_SEQUENCE_DELAY_15_SEC

        if beeps_pattern is not None:
            s_thread = threading.Thread(target=BeepsPatternThread.beeps_thread, daemon=False,
                                        args=(batx728, beeps_pattern))
            s_thread.start()
            s_thread.join()

    # if flash_curtain_type == FRONT_FLASH:
    # print("Switch pressed (main)", capture_event_flag)
