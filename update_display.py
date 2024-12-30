import time
import cv2
from PyQt6.QtCore import QThread, QObject

import globals
from ConvertScaleFrame import convert_and_scale_frame


def update_display_thread(images_queue, info_queue,
                          exit_event, update_info_sig, update_image_sig,
                          img_win, image_array_hist_signal, focus_meas):
    """ Pull out a frame from the queue and display it on the
        window.label widget.
        Runs as long as the global camera_running flag is True """
    image_q = images_queue
    info_q = info_queue
    ext_event = exit_event
    window = img_win
    update_info_display_signal = update_info_sig
    update_image_signal = update_image_sig
    focus_measure = focus_meas

    thread_running = True

    print("update frame thread started")

    frame_num = 0
    info_string = None

    while thread_running:
        if not image_q.empty():
            # There is a new frame out of queue
            frame = image_q.get(block=False)
            if frame.any():
                # The new frame i not empty
                # print("New frame)")
                # window.label.setText(str(frame_num))
                # Convert frame to QPixmap
                # Mark the focus rectangle
                if not focus_measure.get_focus_mode() == globals.FOCUS_TYPE_NONE:
                    start_x, end_x, start_y, end_y = focus_measure.get_focus_center_window_points(frame)
                    cv2.rectangle(frame, (start_x ,start_y), (end_x, end_y), (0, 0, 255), 1)

                pix, scale = convert_and_scale_frame(frame, window.width(), window.height())

                update_image_signal.emit_signal(pix)

                if frame_num % 10 == 0:
                    # print(frame)
                    image_array_hist_signal.emit_signal(frame)
                    if not focus_measure.get_focus_mode() == globals.FOCUS_TYPE_NONE:
                        focus = focus_measure.get_focus_measure_center(frame,
                                                                       focus_measure.get_window_width(),
                                                                       focus_measure.get_window_height())
                        # print("Focus level: ", focus)
                        blur_message = globals.DEFAULT_CAMERA_FOCUS[:5] + '{:.0f}'.format(focus)
                        update_info_display_signal.emit_signal(blur_message)
                    else:
                        blur_message = globals.DEFAULT_CAMERA_FOCUS[:5] + " ---"
                        update_info_display_signal.emit_signal(blur_message)

                frame_num = frame_num + 1
            else:
                print("frame empty")
        else:
            time.sleep(0.02)
            # print("Q is empty")

        if not info_queue.empty():
            info_string = info_q.get()
            if len(info_string) > 0:
                update_info_display_signal.emit_signal(info_string)

        # if shoot_switch_event.is_set():
        #     shoot_switch_event.clear()
        #     main_window_management.shoot_switch_pressed()

        if ext_event.is_set():
            thread_running = False

    print("Update frame exiting...")


class Update_Frame_QtThread(QObject):
    pass
