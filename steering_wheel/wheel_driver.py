import time
import threading

from evdev import UInput, ecodes, AbsInfo
import odrive
from odrive.enums import ControlMode, AxisState, InputMode

from steering_wheel.models import WheelDriverSettings, Box
from steering_wheel import number_utils

class SteeringInfo:
    def __init__(self):
        self.last_steering = 0 # last steering unfiltered
        self.last_steering_time = None
        self.steering = 0
        self.steering_time = None

capabilties = {
    ecodes.EV_FF:  [ecodes.FF_AUTOCENTER, ecodes.FF_CONSTANT, ecodes.FF_CUSTOM, ecodes.FF_DAMPER, ecodes.FF_EFFECT_MAX, ecodes.FF_EFFECT_MIN, ecodes.FF_FRICTION, ecodes.FF_GAIN, ecodes.FF_INERTIA, ecodes.FF_MAX, ecodes.FF_MAX_EFFECTS, ecodes.FF_PERIODIC, ecodes.FF_RAMP, ecodes.FF_RUMBLE, ecodes.FF_SAW_DOWN, ecodes.FF_SAW_UP, ecodes.FF_SINE, ecodes.FF_SPRING, ecodes.FF_SINE, ecodes.FF_SQUARE],
    ecodes.EV_KEY: [ecodes.KEY_A, ecodes.KEY_B, ecodes.BTN_0, ecodes.BTN_1, ecodes.BTN_2, ecodes.BTN_3, ecodes.BTN_4, ecodes.BTN_5, ecodes.BTN_6, ecodes.BTN_7, ecodes.BTN_8, ecodes.BTN_9],
    ecodes.EV_ABS: [ecodes.ABS_X, ecodes.ABS_Y, ecodes.ABS_RX, ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y,
        (ecodes.ABS_Z, AbsInfo(value=0, min=0, max=0xffff, fuzz=0, flat=0, resolution=0))] # this is the one that we actually care about
}

class WheelDriver:
    paused = True
    disconnected = False

    def __init__(self, settings_box: Box[WheelDriverSettings]):
        self.settings_box = settings_box
        
    def run(self):
        print('Starting wheel...')

        self.find_odrive()

        self.running = True
        if not self.settings_box.value.odrive_settings.start_odrive_paused:
            self.unpause_odrive()
        self.steering_info = SteeringInfo()

        self.device = UInput(capabilties, name='Evdev FFB Wheel', version=0x3)
        time.sleep(1)
        self.send_random_events()

        t = threading.Thread(target=lambda: self.input_loop())
        t.start()

        try:
            self.receive_ffb_loop()
        except KeyboardInterrupt:
            self.device.close()

    def find_odrive(self):
        print('Searching for odrive...')
        self.odrv0 = None
        try:
            self.odrv0 = odrive.find_any(timeout=10)
        except TimeoutError:
            print('Failed to find odrive, please check it is plugged in and accessible from other programs')
            return
        
    def setup_odrive(self):
        self.odrv0.axis0.controller.config.control_mode = ControlMode.TORQUE_CONTROL
        self.odrv0.axis0.controller.config.input_mode = InputMode.PASSTHROUGH
        self.odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
    
    def clear_errors(self):
        self.odrv0.clear_errors()
        self.odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL

    @property
    def active(self):
        return not self.paused and not self.disconnected
    


    def pause_odrive(self):
        self.odrv0.axis0.requested_state = AxisState.IDLE
        self.paused = True

    def unpause_odrive(self):
        self.setup_odrive()
        self.paused = False

    def disconnect_odrive(self):
        old_val = self.paused
        self.pause_odrive()
        self.paused = old_val
        
        del self.odrv0
        self.odrv0 = None
        self.disconnected = True

    def reconnect_odrive(self):
        self.find_odrive()
        if not self.paused:
            self.unpause_odrive()
        self.disconnected = False

    def send_random_events(self):
        '''
        Send random events to make steam recognise as an input device
        '''
        self.device.write(ecodes.EV_ABS, ecodes.ABS_X, 0)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_Y, 0)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_Z, 0)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_RX, 0)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_HAT0X, 0)
        self.device.write(ecodes.EV_ABS, ecodes.ABS_HAT0Y, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_0, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_1, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_2, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_3, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_4, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_5, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_6, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_7, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_8, 0)
        self.device.write(ecodes.EV_KEY, ecodes.BTN_9, 0)
    
    def input_loop(self):
        '''
        Loop that handles getting input from odrive and sending it to the game
        '''

        while self.running:
            if not self.active:
                time.sleep(0.1)
                continue

            now = time.perf_counter()

            rotations = self.odrv0.axis0.pos_estimate

            self.steering_info.last_steering = self.steering_info.steering
            self.steering_info.last_steering_time = self.steering_info.steering_time

            self.steering_info.steering_time = now
            self.steering_info.steering = rotations


            latency_adjusted = rotations
            # apply a feedforward to make it look as if there is less latency so you don't get annoyed
            if self.steering_info.last_steering_time is not None:
                vel = (rotations - self.steering_info.last_steering) / (self.steering_info.steering_time - self.steering_info.last_steering_time)
                latency_adjusted += vel * self.settings_box.value.ffb_profile.latency_compensation

            endpoint = self.settings_box.value.ffb_profile.total_rotations / 2
            steering_value = number_utils.map_value(latency_adjusted, -endpoint, endpoint, 0, 0xffff)
            self.device.write(ecodes.EV_ABS, ecodes.ABS_Z, int(steering_value))
            self.device.write(ecodes.EV_SYN, ecodes.SYN_REPORT, 0)
            time.sleep(0.01) # todo: should this be smaller or adjustable

    def receive_ffb_loop(self):
        '''
        Loop that handles receiving ffb and sending it to odrive
        '''

        for event in self.device.read_loop():
            if not self.active:
                time.sleep(0.1)
                continue

            if event.type != ecodes.EV_UINPUT:
                continue

            if event.code == ecodes.UI_FF_UPLOAD:
                upload = self.device.begin_upload(event.value)
                upload.retval = 0

                const = upload.effect.u.ff_constant_effect
                raw_force = const.level

                self.device.end_upload(upload)

                self.apply_force(raw_force)

                if self.odrv0.axis0.current_state != AxisState.CLOSED_LOOP_CONTROL:
                    print(f'Disarm: {self.odrv0.axis0.disarm_reason}')
                    if self.settings_box.value.odrive_settings.ignore_odrive_errors:
                        time.sleep(0.3)
                        self.clear_errors()
                        print("forcing odrive back on")

            elif event.code == ecodes.UI_FF_ERASE:
                erase = self.device.begin_erase(event.value)
                print(f'[erase] effect_id {erase.effect_id}')

                erase.retval = 0
                self.device.end_erase(erase)
            
            else:
                print(f'Unused event code: {event.code}')


    def apply_force(self, raw_force: float):
        '''
        Once a force value is gotten, actually do the processing on it
        '''

        profile = self.settings_box.value.ffb_profile

        scaled_force = raw_force * profile.sensitivity * 0.001 # convert from millinm to nm? Was getting constant clipping without this
        damped_force = scaled_force
        if self.steering_info.last_steering_time is not None:
            damped_force += (self.steering_info.last_steering - self.steering_info.steering) / (self.steering_info.steering_time - self.steering_info.last_steering_time) * profile.damping * 0.0001
        
        if self.settings_box.value.odrive_settings.print_ffb_debug:
            print('------------')
            print(f'Raw force:    {raw_force:<8}')
            print(f'Scaled force: {scaled_force:<8}')
            print(f'Damped force: {damped_force:<8}    (damping is {damped_force - scaled_force:<8})')
        

        self.odrv0.axis0.controller.input_torque = damped_force
        self.odrv0.axis0.watchdog_feed()