from multiprocessing import Event

from PIL import Image
from picamera2 import Picamera2, Preview, Controls
import threading
import time
import subprocess
import psutil

import BeepsPatternThread
from GetScaleStoredImage import get_scale_stored_image
from ShootingThread import shooting_thread
from x1201Bat import BatX1201
# import globals
# from ConfigurationManager import ConfigurationManager
from CameraControlsManager import CameraControlsManager
from SendInfoMessages import send_info_messages
from GrabImage import grab_image
from FilesHandling import *

captured_images_files_directory = ""
captured_images_file_name = ""
captured_images_file_extension = ""

capture_event_flag = False
camera_controls = None
capture_config = None

picam2 = None


def my_pre_callback():
    print("Precallback")


def my_post_callback():
    print("Postcallback")


def short_beep():
    #    global batX728

    beeps_pattern = globals.BEEPS_SEQUENCE_1_SHORT

    """
    s_thread = threading.Thread(target=BeepsPatternThread.beeps_thread, daemon=False,
                                args=(batX728, beeps_pattern))
    s_thread.start()
    s_thread.join()
    """


def pressed_callback(channel):
    """ Called when the shooting switch is pressed. """
    print("Pressed callback ", time.time())


def released_callback(channel):
    """ Called when the shooting switch is released. """
    # print("Released callback ", time.time())
    pass


def parse_files_message(message):
    global captured_images_files_directory
    global captured_images_file_name
    global captured_images_file_extension

    if len(message) > 3:
        if message[0:2] == globals.DEFAULT_IMAGES_DIR_MSSG[0:2]:
            captured_images_files_directory = message[2:]
            print("Dir ", captured_images_files_directory)
            return

        if message[0:2] == globals.DEFAULT_IMAGE_FILE_NAME_MSSG[0:2]:
            captured_images_file_name = message[2:]
            print("Name ", captured_images_file_name)
            return

        if message[0:2] == globals.DEFAULT_IMAGE_FILE_EXTENSION_MSSG[0:2]:
            captured_images_file_extension = message[2:]
            print("Ext ", captured_images_file_extension)
            return


def set_camera_preview_frame_rate(fps):
    preview_fps = True


def camera_grab_process(images_queue, info_queue, files_queue, conf_mssg_q,
                        shoot_event, released_event, grab_frame_event, exit_event,
                        pause_grab_event, resume_grab_event,
                        width, height, frame_rate):
    """ This process runs in the background and grab frame from the camera
        as long as the global camera_running flag is True.
        Grabbed frames are put on the queue.
        Utilizes the x728Bat ups interface for monitoring the batteries' status. """
    image_q = images_queue
    info_q = info_queue
    files_management_q = files_queue
    configuration_message_queue = conf_mssg_q
    # camera_config = ConfigurationManager()
    disp_w = width
    disp_h = height
    preview_fps = frame_rate
    ext_event = exit_event
    pause_grabbing_event = pause_grab_event
    resume_grabbing_event = resume_grab_event
    shoot_switch_event = shoot_event
    released_switch_event = released_event
    grab_a_frame_event = grab_frame_event

    # Set to False when the process should be terminated
    thread_exit_event = Event()
    # When True, grabbing should run; when False, grabbing should pause
    grabbing_active = True

    process_running = True

    battery_monitor = BatX1201()
    t_start_bat_monitoring = time.time()
    camera_start_time = time.time()
    frame_rate = 0
    cpu_temp = 40

    # Capture_event_flag
    global capture_event_flag
    global capture_config

    last_bat_capacity = 100

    resume_grabbing_event.clear()

    start_capture_time = 0
    end_capture_time = 0

    print("grab proces started")

    # Start the shooting switch thread
    s_thread = threading.Thread(target=shooting_thread, daemon=True,
                                args=(thread_exit_event,
                                      pressed_callback,
                                      released_callback,
                                      shoot_switch_event,
                                      released_switch_event))
    s_thread.start()

    # Initiate the Picamera2 camera object instance.
    global picam2
    picam2 = Picamera2()
    picam2.options["quality"] = 80
    picam2.preview_configuration.main.size = (disp_w, disp_h)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.controls.FrameRate = preview_fps

    picam2.preview_configuration.align()  # fix the closest standard format
    picam2.configure("preview")

    capture_config = picam2.create_still_configuration()

    global camera_controls
    camera_controls = CameraControlsManager(picam2.preview_configuration, capture_config, picam2)

    picam2.pre_callback = my_pre_callback()
    picam2.post_callback = my_post_callback()

    picam2.start()
    picam2.title_fields = ["ExposureTime", "AnalogueGain"]

    while process_running:
        if grabbing_active:
            # Grab frames from the camera
            t_start = time.time()
            frame = picam2.capture_array()
            if not frame.any():
                print("No frame!")
            else:
                if not image_q.full():
                    image_q.put(frame, block=False)
                    # print(image_q.qsize())
                else:
                    print("Camera images Q is full. Qsize = ", image_q.qsize())
                    time.sleep(0.3)

            t_end = time.time()
            loop_time = t_end - t_start
            frame_rate = 0.9 * frame_rate + 0.1 / loop_time
            # print(frame_rate)
        else:
            # Pause grabbing frames
            if resume_grabbing_event.is_set():
                resume_grab_event.clear()
                grabbing_active = True
                print("Grab Process - Resume Grabbing")
            # Slow down (reduce power in power save mode)
            time.sleep(0.1)

        # Look for a new files related message
        if not files_management_q.empty():
            files_message = files_management_q.get(block=False)
            parse_files_message(files_message)

        # Wait for a "Shoot" event
        # print("loop capture event ", capture_event_flag)
        if capture_event_flag:
            # print("Grab process - shoot")
            if (len(captured_images_files_directory) > 0 and
                    len(captured_images_file_name) > 0 and
                    len(captured_images_file_extension) > 0):

                # print("Capture start ")

                pic_file_full_path = get_next_image_path_and_name(captured_images_files_directory,
                                                                  captured_images_file_name,
                                                                  captured_images_file_extension)

                if True:  # camera_controls.get_still_exposure_time() >= globals.EXPOSURE_BEEPS_MIN_EXPOSURE_VALUE:
                    if camera_controls.get_exposure_beeps_mode() == 2 or \
                            camera_controls.get_exposure_beeps_mode() == 3:
                        # start or start + end
                        short_beep()

                capture_event_flag = False

                start_capture_time = time.time_ns()

                picam2.switch_mode_and_capture_file(capture_config, pic_file_full_path)

                end_capture_time = time.time_ns()
                print("Capture returned", (end_capture_time - start_capture_time) / 1000000000, time.time())

                if camera_controls.get_still_exposure_time() >= globals.EXPOSURE_BEEPS_MIN_EXPOSURE_VALUE:
                    if camera_controls.get_exposure_beeps_mode() == 1 or \
                            camera_controls.get_exposure_beeps_mode() == 3:
                        # end or start + end
                        short_beep()

                # Get captured image
                padded_image = get_scale_stored_image(pic_file_full_path)

                if not image_q.full():
                    image_q.put(padded_image, block=False)

            # Pause grabbing
            grabbing_active = False
            # Clear any residual event (there must be a better way....)
            resume_grabbing_event.clear()

        if ext_event.is_set():
            # Stop the capture process
            process_running = False
            thread_exit_event.set()

        if grab_a_frame_event.is_set():
            grab_a_frame_event.clear()
            grab_image(camera_controls, battery_monitor)
            capture_event_flag = True

        if pause_grabbing_event.is_set():
            # Pause grabbing
            pause_grabbing_event.clear()
            grabbing_active = False

        if not configuration_message_queue.empty():
            config_message = configuration_message_queue.get(block=False)
            if len(config_message) > 0:
                camera_controls.parse_messages(config_message, picam2)
                # Control updates rate must be limited.
                # Rapid updates may cause the PyQt5 lib to crash.
                time.sleep(0.05)

        if time.time() >= t_start_bat_monitoring + globals.HW_INFO_UPDATE_RATE_SEC:
            # Monitor battery state every 10 seconds
            t_start_bat_monitoring = time.time()
            bat_charge = battery_monitor.read_bat_capacity()
            if bat_charge > 100:
                bat_charge = 100

            # Low battery alert
            bat_low_level = 15 - bat_charge
            if bat_low_level > 0 and int(bat_charge) < int(last_bat_capacity):
                last_bat_capacity = bat_charge
                for i in range(0, int(bat_low_level)):
                    # batX728.set_buzzer_on()
                    time.sleep(0.2)
                    # batX728.set_buzzer_off()
                    time.sleep(1)

            bat_voltage = battery_monitor.read_bat_voltage()

            input_power_connected = battery_monitor.get_power_connection_state()

            camera_on_time = time.time() - camera_start_time
            camera_on_time_h = camera_on_time // 3600
            camera_on_time_m = (camera_on_time - camera_on_time_h * 3600) // 60
            camera_on_time_s = (camera_on_time - camera_on_time_h * 3600 - camera_on_time_m * 60) // 1
            camera_on_time_string = '{:02.0f}:{:02.0f}:{:02.0f}'.format(camera_on_time_h,
                                                                        camera_on_time_m,
                                                                        camera_on_time_s)

            cpu_temp = '{:02.0f}'.format(0.8 * float(cpu_temp) +
                                         0.2 * float(subprocess.getoutput("vcgencmd measure_temp|sed 's/[^0-9.]//g'")))

            cpu_usage = str(psutil.cpu_percent())

            exposure_time = picam2.capture_metadata()["ExposureTime"]

            pic_brightness = picam2.capture_metadata()["Lux"]

            analogue_gain = picam2.capture_metadata()["AnalogueGain"]

            send_info_messages(info_q, input_power_connected, bat_charge, bat_voltage,
                               camera_on_time_string, cpu_temp, cpu_usage,
                               exposure_time, pic_brightness, analogue_gain)

    print("Camera proces exiting....")
