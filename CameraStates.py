"""
This class implements the camera main state machine.
Each state is implemented as a State object class.
The camera state machine comprises the following states:
  - Preview State: the default camera state in which the camera display
    presents the 30 fps captured images in medium resolution.
  - Show Captured Image State: in this state, the last high-resolution
    captured image is displayed on the camera display.
  - Show Settings Parameter State: In this state, the user can various
    configuration settings of the camera. Some of the camera configuration
    parameters enable live adjustment, in which the configuration setting
    affects the live preview image (like in the Preview State).
  - Show Images State: In this state, the user can browse and view the captured
    images that are stored on the camera mass-storage.
  - Show Selected Image State: In this state the selected stored image is displayed
    in a full-display mode.
  - Set Interfaces State: In this state, the user can set various camera
    configuration parameters that affect the camera's WiFi and Bluetooth operation.
  - Show Hardware Parameters State: In this state the camera display is used for
    displaying various camera hardware-related parameters, such as CPU temperature
    and utilization, battery voltage and capacity, etc.
  - Power saving state: In this state the CPU activity is reduced to a minimum level.
    It is also desirable to reduce the display power consumption - TBD.
    This state is activated when a no activity timer expires.
    This state transients into the Show Preview state when the user presses the shoot switch or touces the display.

The state transitions are controlled by the system events and the Qt GUI-related Signals (and Slots).

System events include the following events (this list includes only the relevant events):

  - display_clicked_event: set when the user cliks on the display image widget.
  - shoot_event: set when the user press the shooting switch.
  - back_clicked_event: set when the user clicks the "Back" pushbutton.
  - images_clicked_event: set when the user clicks the "Images" pushbutton.
  - interfaces_clicked_event: set when te user clicks the "Interfaces" pushbutton.
  - hw_clicked_event: set when the user clicks the "HW" pushbutton.
  - image_selected_events: set when the user clicks on one of the images on the images browser display.
  - enable_live_param_setting_view_event: when set, the live parameter setting mode is enabled.
  - resume_grabbing_event: when set, the grabbing proces starts again.
  - pause_grabbing_event: when set, the frame grabbing process is paused.
  - grab_frame_event: when set, a high-resolution still image is grabbed and stored.
  - images_done_close_clicked_event: set when the Images dialog "Done" pushbutton is clicked
  - close_the_image_dialog_event: when set, the Images Dialog is closed
  - params_clicked_event: set when the "Settings" pushbutton is pressed
  - no_activity_timer_expired_event: set when the no user activity timer expires

Qt Signals include the following signals:

  - ShowHideImageViewSignal: used to show or hide the image view (label_pix)
  - PressParamsSignal: used to indicate that the "Params" pushbutton was pressed
  - PressBackSignal:  used to indicate that the "Back" pushbutton was pressed
  - ReopenImagesSignal: used to indicate that the "Images" pushbutton was pressed

"""

import threading
import time

STATE_INIT = 0
STATE_SHOW_PREVIEW = 1
STATE_SHOW_CAPTURED_IMAGE = 2
STATE_SHOW_PARAMS_SETTINGS = 3
STATE_SHOW_IMAGES = 4
STATE_SHOW_SELECTED_IMAGE = 5
STATE_SHOW_HARDWARE_PARAMS = 6
STATE_SHOW_INTERFACES_SETTINGS = 7
STATE_POWER_SAVE = 8

_DEFAULT_STATE = STATE_SHOW_PREVIEW

"""
STATE_EVENT_NONE = -1
STATE_EVENT_SHOOT = 0
STATE_EVENT_CLICK_ON_DISPLAY = 1
STATE_EVENT_CLICK_ON_BACK = 2
STATE_EVENT_DONE_CLOSE = 3
STATE_EVENT_CLICK_ON_IMAGES = 4
STATE_EVENT_CLICK_ON_VIEWED_IMAGE = 5
STATE_EVENT_CLICK_ON_HW = 6
STATE_EVENT_CLICK_ON_INTERFACES = 7
"""


def clear_queue(queue):
    while not queue.empty():
        queue.get(block=False)


class _State():
    """ This class implements a specific State of the state machine """

    def __init__(self, parent_state_machine=None,
                 active=False, state_id=0,
                 configuration=None):
        # State identifier
        self.state_id = state_id
        self.parent_state_machine = parent_state_machine
        # Indicates if the state is active.
        # May be initiated as active without executing the state-entry procedure
        self.active = active
        self.event = None
        self.event_name = "event"
        self.configuration_manager = configuration

    def state_is_active(self):
        """ Returns True if the state is active and False if not """
        return self.active

    def get_state_id(self):
        """ Returns the state ID """
        return self.state_id

    def on_state_enter(self):
        """ Executed when the state is activated """
        pass

    def on_state_exit(self):
        """ Executed wen the state is deactivated """
        pass

    def activate(self, on_enter=False):
        """ Activates the state and execute the state activation procedure if the on_enter parameter is True """
        self.active = True
        if on_enter:
            self.on_state_enter()

    def deactivate(self, on_exit=False):
        """ Deactivates the state and execute the state deactivation procedure if the on_exit parameter is True """
        self.active = False
        if on_exit:
            self.on_state_exit()

    def on_new_event(self, event=None, event_name="event"):
        pass


class _ShowPreviewState(_State):
    """ In this state the captured images stream is displayed ("Viewfinder"). """

    def on_state_enter(self):
        # Resume the pictures grabbing
        self.parent_state_machine.sys_events_dictionary["resume_grabbing_event"].set()
        # Show the image view
        self.parent_state_machine.custom_signals_dictionary["ShowHideImageViewSignal"].emit_signal(True)

    def on_new_event(self, event=None, event_name="event"):
        self.event = event
        self.event_name = event_name

        print("Preview", self.event_name)

        # Act upon received event
        if self.event_name == "display_clicked_event":
            # Switch to the show parameters state
            self.parent_state_machine.set_state(STATE_SHOW_PARAMS_SETTINGS)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_params_settings_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display
            self.parent_state_machine.custom_signals_dictionary["PressParamsSignal"].emit_signal()

        elif self.event_name == "shoot_event":
            # Switch to the show captured image state
            self.parent_state_machine.set_state(STATE_SHOW_CAPTURED_IMAGE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_captured_image_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            self.parent_state_machine.sys_events_dictionary["grab_frame_event"].set()
            # Save last configuration
            if self.configuration_manager.get_configuration_was_changed:
                self.configuration_manager.save_configuration()
                self.configuration_manager.set_last_configuration_was_saved()
                print("Last configuration was saved.")

        elif self.event_name == "no_activity_timer_expired_event":
            # Switch to Power Save state
            self.parent_state_machine.set_state(STATE_POWER_SAVE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.power_save_state)
            self.parent_state_machine.active_state.activate(on_enter=True)


class _ShowCapturedImageState(_State):
    """ In this state the captured image is displayed. """

    def on_state_enter(self):
        # Stop frame grabbing
        self.parent_state_machine.sys_events_dictionary["pause_grabbing_event"].set()
        # Show the image view
        self.parent_state_machine.custom_signals_dictionary["ShowHideImageViewSignal"].emit_signal(True)

    def on_new_event(self, event=None, event_name="event"):
        self.event = event
        self.event_name = event_name

        print("Captured Image", self.event_name, time.time())

        # Act upon received event
        if self.event_name == "shoot_event":
            # Switch to the show preview state
            self.parent_state_machine.set_state(STATE_SHOW_PREVIEW)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_preview_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to preview
            self.parent_state_machine.custom_signals_dictionary["PressBackSignal"].emit_signal()

        elif self.event_name == "display_clicked_event":
            # Switch to the show preview state
            self.parent_state_machine.set_state(STATE_SHOW_PREVIEW)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_preview_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to preview
            self.parent_state_machine.custom_signals_dictionary["PressBackSignal"].emit_signal()

        elif self.event_name == "no_activity_timer_expired_event":
            # Switch to Power Save state
            self.parent_state_machine.set_state(STATE_POWER_SAVE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.power_save_state)
            self.parent_state_machine.active_state.activate(on_enter=True)


class _ShowParamsSettingsState(_State):
    """ In this state the setting parameters dialog is displayed. """

    def on_state_enter(self):
        # Stop frame grabbing
        self.parent_state_machine.sys_events_dictionary["pause_grabbing_event"].set()
        # Hide the image view
        self.parent_state_machine.custom_signals_dictionary["ShowHideImageViewSignal"].emit_signal(False)

    def on_new_event(self, event=None, event_name="event"):
        self.event = event
        self.event_name = event_name

        print("Params", self.event_name)

        # Act upon received event
        if self.event_name == "shoot_event" or self.event_name == "back_clicked_event":
            # Switch to the show preview state
            self.parent_state_machine.set_state(STATE_SHOW_PREVIEW)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_preview_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to preview
            self.parent_state_machine.custom_signals_dictionary["PressBackSignal"].emit_signal()

        elif self.event_name == "enable_live_param_setting_view_event":
            # Resume frame grabbing
            self.parent_state_machine.sys_events_dictionary["resume_grabbing_event"].set()
            # Show the image view
            self.parent_state_machine.custom_signals_dictionary["ShowHideImageViewSignal"].emit_signal(True)

        elif self.event_name == "images_clicked_event":
            # Switch to the show images state
            self.parent_state_machine.set_state(STATE_SHOW_IMAGES)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_images_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "hw_clicked_event":
            # Switch to the show hw params state
            self.parent_state_machine.set_state(STATE_SHOW_HARDWARE_PARAMS)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_hw_params_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "interfaces_clicked_event":
            # Switch to the show interfaces settings state
            self.parent_state_machine.set_state(STATE_SHOW_INTERFACES_SETTINGS)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_interfaces_settings_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "no_activity_timer_expired_event":
            # Switch to Power Save state
            self.parent_state_machine.set_state(STATE_POWER_SAVE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.power_save_state)
            self.parent_state_machine.active_state.activate(on_enter=True)


class _ShowImagesState(_State):
    """ In this state the user can brows the stored captured images and select one to show. """

    def on_state_enter(self):
        # Stop frame grabbing
        self.parent_state_machine.sys_events_dictionary["pause_grabbing_event"].set()
        # Show the image view
        self.parent_state_machine.custom_signals_dictionary["ShowHideImageViewSignal"].emit_signal(True)

    def on_new_event(self, event=None, event_name="event"):
        self.event = event
        self.event_name = event_name

        print("Images", self.event_name)

        # Act upon received event
        if (self.event_name == "shoot_event" or
                self.event_name == "images_done_close_clicked_event" or
                self.event_name == "close_the_image_dialog_event"):
            # Switch to the show preview state
            self.parent_state_machine.set_state(STATE_SHOW_PREVIEW)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_preview_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to preview
            self.parent_state_machine.custom_signals_dictionary["PressBackSignal"].emit_signal()

        elif self.event_name == "image_selected_event":
            # Switch to the show selected image state
            self.parent_state_machine.set_state(STATE_SHOW_SELECTED_IMAGE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_selected_image_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Stop frame grabbing
            self.parent_state_machine.sys_events_dictionary["pause_grabbing_event"].set()

        elif self.event_name == "no_activity_timer_expired_event":
            # Switch to Power Save state
            self.parent_state_machine.set_state(STATE_POWER_SAVE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.power_save_state)
            self.parent_state_machine.active_state.activate(on_enter=True)


class _ShowSelectedImageState(_State):
    """ In this state the selected stored image is displayed. """

    def on_state_enter(self):
        # Stop frame grabbing
        self.parent_state_machine.sys_events_dictionary["pause_grabbing_event"].set()
        # Show the image view
        self.parent_state_machine.custom_signals_dictionary["ShowHideImageViewSignal"].emit_signal(True)

    def on_new_event(self, event=None, event_name="event"):
        self.event = event
        self.event_name = event_name

        print("Selected Image", self.event_name)

        # Act upon received event
        if self.event_name == "shoot_event":
            # Switch to the show preview state
            self.parent_state_machine.set_state(STATE_SHOW_PREVIEW)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_preview_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to preview
            self.parent_state_machine.custom_signals_dictionary["PressBackSignal"].emit_signal()

        elif self.event_name == "display_clicked_event":
            # Switch back to the show images state
            self.parent_state_machine.set_state(STATE_SHOW_IMAGES)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_images_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to images
            self.parent_state_machine.custom_signals_dictionary["ReopenImagesSignal"].emit_signal()

        elif self.event_name == "no_activity_timer_expired_event":
            # Switch to Power Save state
            self.parent_state_machine.set_state(STATE_POWER_SAVE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.power_save_state)
            self.parent_state_machine.active_state.activate(on_enter=True)


class _ShowHwParamsState(_State):
    """ In this sate the HW parameters are displayed. """

    def on_state_enter(self):
        # Stop frame grabbing
        self.parent_state_machine.sys_events_dictionary["pause_grabbing_event"].set()
        # Hide the image view
        self.parent_state_machine.custom_signals_dictionary["ShowHideImageViewSignal"].emit_signal(False)

    def on_new_event(self, event=None, event_name="event"):
        self.event = event
        self.event_name = event_name

        print("HW Params", self.event_name)

        # Act upon received event
        if self.event_name == "shoot_event" or self.event_name == "back_clicked_event":
            # Switch to the show preview state
            self.parent_state_machine.set_state(STATE_SHOW_PREVIEW)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_preview_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to preview
            self.parent_state_machine.custom_signals_dictionary["PressBackSignal"].emit_signal()

        elif self.event_name == "interfaces_clicked_event":
            # Switch to the show interfaces settings state
            self.parent_state_machine.set_state(STATE_SHOW_INTERFACES_SETTINGS)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_interfaces_settings_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "params_clicked_event":
            # Switch to the show params settings state
            self.parent_state_machine.set_state(STATE_SHOW_PARAMS_SETTINGS)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_params_settings_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "images_clicked_event":
            # Switch to the show images state
            self.parent_state_machine.set_state(STATE_SHOW_IMAGES)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_images_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "no_activity_timer_expired_event":
            # Switch to Power Save state
            self.parent_state_machine.set_state(STATE_POWER_SAVE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.power_save_state)
            self.parent_state_machine.active_state.activate(on_enter=True)


class _ShowInterfacesSettingsState(_State):
    """ In this state the interfaces settings dialog is displayed. """

    def on_state_enter(self):
        # Stop frame grabbing
        self.parent_state_machine.sys_events_dictionary["pause_grabbing_event"].set()
        # Hide the image view
        self.parent_state_machine.custom_signals_dictionary["ShowHideImageViewSignal"].emit_signal(False)

    def on_new_event(self, event=None, event_name="event"):
        self.event = event
        self.event_name = event_name

        print("Interfaces", self.event_name)

        # Act upon received event
        if self.event_name == "shoot_event" or self.event_name == "back_clicked_event":
            # Switch to the show preview state
            self.parent_state_machine.set_state(STATE_SHOW_PREVIEW)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_preview_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to preview
            self.parent_state_machine.custom_signals_dictionary["PressBackSignal"].emit_signal()

        elif self.event_name == "params_clicked_event":
            # Switch to the show params settings state
            self.parent_state_machine.set_state(STATE_SHOW_PARAMS_SETTINGS)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_params_settings_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "hw_clicked_event":
            # Switch to the show hw params state
            self.parent_state_machine.set_state(STATE_SHOW_HARDWARE_PARAMS)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_hw_params_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "images_clicked_event":
            # Switch to the show images state
            self.parent_state_machine.set_state(STATE_SHOW_IMAGES)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_images_state)
            self.parent_state_machine.active_state.activate(on_enter=True)

        elif self.event_name == "no_activity_timer_expired_event":
            # Switch to Power Save state
            self.parent_state_machine.set_state(STATE_POWER_SAVE)
            self.parent_state_machine.set_active_state(self.parent_state_machine.power_save_state)
            self.parent_state_machine.active_state.activate(on_enter=True)


class _PowerSaveState(_State):
    def on_state_enter(self):
        # Stop grabbing process
        self.parent_state_machine.sys_events_dictionary["pause_grabbing_event"].set()
        # Put here display dimming

    def on_new_event(self, event=None, event_name="event"):
        self.event = event
        self.event_name = event_name

        print("Power Save", self.event_name)

        # Act upon received event
        if (self.event_name == "shoot_event" or self.event_name == "display_clicked_event" or
                               self.event_name == "exit_power_save_state_event"):
            # Switch to the show preview state
            self.parent_state_machine.set_state(STATE_SHOW_PREVIEW)
            self.parent_state_machine.set_active_state(self.parent_state_machine.show_preview_state)
            self.parent_state_machine.active_state.activate(on_enter=True)
            # Switch the display back to preview
            self.parent_state_machine.custom_signals_dictionary["PressBackSignal"].emit_signal()

            # Resume the pictures grabbing
            self.parent_state_machine.sys_events_dictionary["resume_grabbing_event"].set()

            # Restart power save timer
            self.parent_state_machine.sys_events_dictionary["user_activity_event"].set()

            self.event.clear()


class CameraStateMachine:
    """ This class implements a Finite Events Driven State Machine.
        The states represent the display states as the camera states. """

    def __init__(self, init_state=_DEFAULT_STATE,
                 sys_events_dic=None, custom_sigs_dic=None,
                 images_q=None, configuration=None):
        self.state = init_state
        self.active_state = None
        self.sys_events_dictionary = sys_events_dic
        self.custom_signals_dictionary = custom_sigs_dic
        self.images_queue = images_q
        self.configuration_manger = configuration

        # Create the states objects
        self.show_preview_state = _ShowPreviewState(parent_state_machine=self, active=False,
                                                    state_id=STATE_SHOW_PREVIEW,
                                                    configuration=self.configuration_manger)

        self.show_captured_image_state = _ShowCapturedImageState(parent_state_machine=self, active=False,
                                                                 state_id=STATE_SHOW_CAPTURED_IMAGE)

        self.show_params_settings_state = _ShowParamsSettingsState(parent_state_machine=self, active=False,
                                                                   state_id=STATE_SHOW_PARAMS_SETTINGS)

        self.show_images_state = _ShowImagesState(parent_state_machine=self, active=False,
                                                  state_id=STATE_SHOW_IMAGES)

        self.show_selected_image_state = _ShowSelectedImageState(parent_state_machine=self, active=False,
                                                                 state_id=STATE_SHOW_SELECTED_IMAGE)

        self.show_hw_params_state = _ShowHwParamsState(parent_state_machine=self, active=False,
                                                       state_id=STATE_SHOW_HARDWARE_PARAMS)

        self.show_interfaces_settings_state = _ShowInterfacesSettingsState(parent_state_machine=self,
                                                                           active=False,
                                                                           state_id=STATE_SHOW_INTERFACES_SETTINGS)

        self.power_save_state = _PowerSaveState(parent_state_machine=self,
                                                active=False,
                                                state_id=STATE_POWER_SAVE)

        # Set and activate the initial state class
        if self.state == STATE_SHOW_PREVIEW:
            self.active_state = self.show_preview_state
        elif self.state == STATE_SHOW_CAPTURED_IMAGE:
            self.active_state = self.show_captured_image_state
        elif self.state == STATE_SHOW_PARAMS_SETTINGS:
            self.active_state = self.show_params_settings_state
        elif self.state == STATE_SHOW_IMAGES:
            self.active_state = self.show_images_state
        elif self.state == STATE_SHOW_SELECTED_IMAGE:
            self.active_state = self.show_selected_image_state
        elif self.state == STATE_SHOW_HARDWARE_PARAMS:
            self.active_state = self.show_hw_params_state
        elif self.state == STATE_SHOW_INTERFACES_SETTINGS:
            self.active_state = self.show_interfaces_settings_state
        elif self.state == STATE_POWER_SAVE:
            self.active_state = self.power_save_state

        self.active_state.activate(on_enter=False)

        # Start the events thread
        self.capture_events_thread_is_running = True
        self.capture_events_thread = threading.Thread(target=self.capture_events_thread, daemon=True,
                                                      args=(self.sys_events_dictionary,))
        self.capture_events_thread.start()
        # self.capture_events_thread.join(0.01)

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_active_state(self, active_state):
        self.active_state = active_state

    def on_new_event(self, event, event_name):
        event.clear()
        self.active_state.on_new_event(event, event_name)

    def capture_events_thread(self, events):
        """ This thread listens to the system events.
            When a relevant system event is set, it generates a state machine event. """
        print("State machine events thread is running.")
        while self.capture_events_thread_is_running:
            for k, event in events.items():
                if event.is_set():
                    self.on_new_event(event, k)

                time.sleep(0.05)


if __name__ == "__main__":
    print("Testing CameraStates")

    csm = CameraStateMachine(STATE_SHOW_PREVIEW)
