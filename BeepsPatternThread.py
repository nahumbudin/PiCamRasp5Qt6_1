import threading
import time

from x728Bat import BatX728
import globals


def beeps_thread(x728_bord_handler, beeps_pattern):
    """ This thread generates a beeps pattern using the x728 board buzzer.
        Beeps sequence is started by running the thread, that generates a single beeps pattern and exits.
        Beeps pattern parameter is a list of tuple: [(), (), (),      ()]
        Each tuple represents a segment or multiple segments of a beep-on period and a beep-off period.
        Each tuple contains 3 parameters (beep_on_time_ms, beep_off_time_ms, repetition_times)
        For example (500, 500, 3) will generate a sequence of 3 times a 0.5sec beep-on and o.5 sec beep off.
        """

    x728_bord_handler.set_buzzer_off()

    for time_on_ms, time_off_ms, repetition_times in beeps_pattern:
        if repetition_times < 1:
            repetition_times = 1

        if time_on_ms < globals.BEEPS_MINIMUM_TIME:
            time_on_ms = globals.BEEPS_MINIMUM_TIME
        elif time_on_ms > globals.BEEPS_MAXIMUM_TIME:
            time_on_ms = globals.BEEPS_MAXIMUM_TIME

        if time_off_ms < globals.BEEPS_MINIMUM_TIME:
            time_off_ms = globals.BEEPS_MINIMUM_TIME
        elif time_off_ms > globals.BEEPS_MAXIMUM_TIME:
            time_off_ms = globals.BEEPS_MAXIMUM_TIME

        rep_times = repetition_times
        time_on_ms /= 1000
        time_off_ms /= 1000

        while rep_times > 0:
            x728_bord_handler.set_buzzer_on()
            time.sleep(time_on_ms)
            x728_bord_handler.set_buzzer_off()
            time.sleep(time_off_ms)

            rep_times -= 1


if __name__ == "__main__":
    batX728 = BatX728()

    pattern = globals.BEEPS_ONGOING_SEQUENCE_DELAY_15_SEC

    while True:
        s_thread = threading.Thread(target=beeps_thread, daemon=False,
                                    args=(batX728, pattern))
        s_thread.start()
        s_thread.join()

        time.sleep(1)
