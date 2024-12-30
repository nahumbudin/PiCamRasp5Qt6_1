import time

thread_is_running = True
timer_expiration_time = 60
timer_start_time = time.time()
expired_event_set = False
power_save_mode_enabled = True


def enable_power_save_mode():
    """ This function enables the timer operation by overriding the expiration event generation """
    global power_save_mode_enabled

    print("Enable power save mode")
    power_save_mode_enabled = True


def disable_power_save_mode():
    """ This function enables the timer operation by overriding the expiration event generation """
    global power_save_mode_enabled

    print("Disable power save mode")
    power_save_mode_enabled = False


def restart_power_save_timer(exp_time=60):
    global timer_expiration_time
    global timer_start_time
    global expired_event_set

    timer_expiration_time = exp_time
    timer_start_time = time.time()
    expired_event_set = False


def disable_timer_expiration_event():
    """ Calling this function will disable the expiration event (the timer thread will keep running. """
    global expired_event_set
    # This will prevent the event re-emission.
    expired_event_set = True


def power_save_timer_thread(initial_time, restart_event, expired_event, exit_event):
    """ This thread runs a no activity timer.
        Any user activity resets the timer.
        If the no activity timer expires, the thread emits a no activity event. """

    global thread_is_running
    global timer_expiration_time
    global timer_start_time
    global expired_event_set
    global power_save_mode_enabled

    restart_power_save_timer(initial_time)

    thread_is_running = True

    print("Power save timer thread started!")

    while thread_is_running:

        if restart_event.is_set():
            print("Reset power save timer")
            restart_power_save_timer(timer_expiration_time)
            restart_event.clear()

        if exit_event.is_set():
            thread_is_running = False
            print("Power save thread exiting...")

        if not expired_event_set and power_save_mode_enabled:
            # print("Power save time tick", time.time() - timer_start_time, timer_expiration_time, expired_event_set)
            if time.time() - timer_start_time >= timer_expiration_time:
                print("Power save timeout expired!")
                expired_event_set = True
                expired_event.set()

        time.sleep(0.1)
