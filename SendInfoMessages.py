import globals


def send_info_messages(info_q, in_pwr=1, bat_c=0, bat_v=0,
                       cam_time_on="", cpu_tmp="", cpu_use="",
                       exp_time=0, pic_bright=0, analog_gain=0):
    """ This function sends information messages from he grabbing process to the main Qt process. """
    if in_pwr == 1:
        charging_message = globals.DEFAULT_CHARGING_STATUS[:5] + '1'
        if info_q.qsize() < 40:
            info_q.put(charging_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())
    elif in_pwr == 0:
        charging_message = globals.DEFAULT_CHARGING_STATUS[:5] + '0'
        if info_q.qsize() < 40:
            info_q.put(charging_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())

    if bat_c > 0:
        bat_charge_message = globals.DEFAULT_BAT_CAPACITY[:5] + '{:.0f}'.format(bat_c)
        if info_q.qsize() < 40:
            info_q.put(bat_charge_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())

    if bat_v > 0:
        bat_voltage_message = globals.DEFAULT_BAT_VOLTAGE[:5] + '{:.2f}'.format(bat_v)
        if info_q.qsize() < 40:
            info_q.put(bat_voltage_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())

    if len(cam_time_on) > 0:
        cam_on_time_message = globals.DEFAULT_CAMERA_ON_TIME[:5] + cam_time_on
        if info_q.qsize() < 40:
            info_q.put(cam_on_time_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())
            process_running = False

    if len(cpu_tmp) > 0:
        cpu_temp_message = globals.DEFAULT_CPU_TEMP[:5] + cpu_tmp
        if info_q.qsize() < 40:
            info_q.put(cpu_temp_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())

    if len(cpu_use) > 0:
        cpu_usage_message = globals.DEFAULT_CPU_USAGE[:5] + cpu_use
        if info_q.qsize() < 40:
            info_q.put(cpu_usage_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())

    if exp_time > 0:
        exp_time_message = globals.DEFAULT_CAMERA_EXP_TIME[:5] + '{:.0f}'.format(exp_time)
        if info_q.qsize() < 40:
            info_q.put(exp_time_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())

    if pic_bright > 0:
        pic_brightness_message = globals.DEFAULT_CAMERA_LUX[:5] + '{:.0f}'.format(pic_bright)
        if info_q.qsize() < 40:
            info_q.put(pic_brightness_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())

    if analog_gain > 0:
        analog_gain_message = globals.DEFAULT_CAMERA_GAIN[:5] + '{:.0f}'.format(analog_gain)
        if info_q.qsize() < 40:
            info_q.put(analog_gain_message, block=False)
        else:
            print("Info images Q is full. Qsize = ", info_q.qsize())