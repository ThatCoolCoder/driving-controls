import time
import threading
import dataclasses
import json

from evdev import UInput, categorize, ecodes, AbsInfo
import odrive
from odrive.enums import ControlMode, AxisState, InputMode

from steering_wheel.models import WheelDriverSettings, Box
from steering_wheel import number_utils

class SteeringInfo:
    def __init__(self):
        self.last_steering = None
        self.last_steering_time = None
        self.steering = None
        self.steering_time = None

capabilties = {
    ecodes.EV_FF:  [ecodes.FF_AUTOCENTER, ecodes.FF_CONSTANT, ecodes.FF_CUSTOM, ecodes.FF_DAMPER, ecodes.FF_EFFECT_MAX, ecodes.FF_EFFECT_MIN, ecodes.FF_FRICTION, ecodes.FF_GAIN, ecodes.FF_INERTIA, ecodes.FF_MAX, ecodes.FF_MAX_EFFECTS, ecodes.FF_PERIODIC, ecodes.FF_RAMP, ecodes.FF_RUMBLE, ecodes.FF_SAW_DOWN, ecodes.FF_SAW_UP, ecodes.FF_SINE, ecodes.FF_SPRING, ecodes.FF_SINE, ecodes.FF_SQUARE],
    ecodes.EV_KEY: [ecodes.KEY_A, ecodes.KEY_B, ecodes.BTN_0, ecodes.BTN_1, ecodes.BTN_2, ecodes.BTN_3, ecodes.BTN_4, ecodes.BTN_5, ecodes.BTN_6, ecodes.BTN_7, ecodes.BTN_8, ecodes.BTN_9],
    ecodes.EV_ABS: [ecodes.ABS_X, ecodes.ABS_Y, ecodes.ABS_RX, ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y,
        (ecodes.ABS_Z, AbsInfo(value=0, min=0, max=0xffff, fuzz=0, flat=0, resolution=0))] # this is the one that we actually care about
}

running = True

def main(settings_box: Box[WheelDriverSettings]):
    '''
    Entry point of the actual wheel program. Uses a box for settings so you can change the settings whenever
    '''

    global running

    print('Starting wheel...')

    print('Searching for odrive...')
    odrv0 = None
    try:
        odrv0 = odrive.find_any(timeout=10)
    except TimeoutError:
        print('Failed to find odrive, please check it is plugged in and accessible from other programs')
        return

    steering_info = SteeringInfo()

    device = UInput(capabilties, name='Evdev FFB Wheel', version=0x3)
    time.sleep(1)
    
    send_random_events(device)

    odrv0.axis0.controller.config.control_mode = ControlMode.TORQUE_CONTROL
    odrv0.axis0.controller.config.input_mode = InputMode.PASSTHROUGH
    odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL

    t = threading.Thread(target=lambda: input_loop(device, odrv0, settings_box, steering_info))
    t.start()

    try:
        receive_ffb_loop(device, odrv0, settings_box, steering_info)
    except KeyboardInterrupt:
        device.close()

def send_random_events(device):
    '''
    Send random events to make steam recognise as an input device
    '''
    device.write(ecodes.EV_ABS, ecodes.ABS_X, 0)
    device.write(ecodes.EV_ABS, ecodes.ABS_Y, 0)
    device.write(ecodes.EV_ABS, ecodes.ABS_Z, 0)
    device.write(ecodes.EV_ABS, ecodes.ABS_RX, 0)
    device.write(ecodes.EV_ABS, ecodes.ABS_HAT0X, 0)
    device.write(ecodes.EV_ABS, ecodes.ABS_HAT0Y, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_0, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_1, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_2, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_3, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_4, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_5, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_6, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_7, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_8, 0)
    device.write(ecodes.EV_KEY, ecodes.BTN_9, 0)

def input_loop(device, odrv0, settings_box: Box[WheelDriverSettings], steering_info: SteeringInfo):
    '''
    Loop that handles getting input from odrive and sending it to the game
    '''

    while running:
        endpoint = settings_box.value.ffb_profile.total_rotations / 2
        now = time.perf_counter()

        val = number_utils.map_value(odrv0.axis0.pos_estimate, -endpoint, endpoint, 0, 0xffff)

        steering_info.last_steering = steering_info.steering
        steering_info.last_steering_time = steering_info.steering_time
        steering_info.steering_time = now
        steering_info.steering = val

        device.write(ecodes.EV_ABS, ecodes.ABS_Z, int(val))
        device.write(ecodes.EV_SYN, ecodes.SYN_REPORT, 0)
        time.sleep(0.01) # todo: should this be smaller or adjustable


def receive_ffb_loop(device, odrv0, settings_box: Box[WheelDriverSettings], steering_info: SteeringInfo):
    '''
    Loop that handles receiving ffb and sending it to odrive
    '''

    for event in device.read_loop():
        if event.type != ecodes.EV_UINPUT:
            continue

        if event.code == ecodes.UI_FF_UPLOAD:
            upload = device.begin_upload(event.value)
            upload.retval = 0

            const = upload.effect.u.ff_constant_effect
            raw_force = const.level

            device.end_upload(upload)

            apply_force(raw_force, odrv0, settings_box, steering_info)

            if odrv0.axis0.current_state != AxisState.CLOSED_LOOP_CONTROL:
                print(odrv0.axis0.disarm_reason)
                if settings_box.value.odrive_settings.ignore_odrive_errors:
                    odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
                    print("forcing odrive back on")

        elif event.code == ecodes.UI_FF_ERASE:
            erase = device.begin_erase(event.value)
            print(f'[erase] effect_id {erase.effect_id}')

            erase.retval = 0
            device.end_erase(erase)
        
        else:
            print(f'Unused event code: {event.code}')


def apply_force(raw_force: float, odrv0, settings_box: Box[WheelDriverSettings], steering_info: SteeringInfo):
    '''
    Once a force value is gotten, actually do the processing on it
    '''

    profile = settings_box.value.ffb_profile

    scaled_force = raw_force * profile.sensitivity * 0.001 # convert from millinm to nm? Was getting constant clipping without this
    damped_force = scaled_force
    if steering_info.last_steering is not None:
        damped_force += (steering_info.last_steering - steering_info.steering) / (steering_info.steering_time - steering_info.last_steering_time) * profile.damping * 0.0001
    
    if settings_box.value.print_ffb_debug:
        print('------------')
        print(f'Raw force:    {raw_force:<8}')
        print(f'Scaled force: {scaled_force:<8}')
        print(f'Damped force: {damped_force:<8}    (damping is {damped_force - scaled_force:<8})')
    

    odrv0.axis0.controller.input_torque = damped_force
    odrv0.axis0.watchdog_feed()