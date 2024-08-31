from odrive.enums import *
import time
import math
import threading
from dataclasses import dataclass

from dataclasses_json import dataclass_json
from evdev import UInput, categorize, ecodes, AbsInfo
import odrive

import ui_debug

@dataclass_json
@dataclass
class Config:
    sensitivity: float = 0.1
    damping: float = 0.1
    total_rotations: float = 4
    ignore_odrive_errors: bool = False
    auto_reread_config: bool = False # useful for dev
    print_ffb_debug: bool = False

class ConfigBox:
    config: Config
    def __init__(self, config: Config):
        self.config = config

class SteeringInfo:
    def __init__(self):
        self.last_steering = None
        self.last_steering_time = None
        self.steering = None
        self.steering_time = None

# events = (uinput.BTN_JOYSTICK,
#     uinput.ABS_X + (0, 255, 0, 0), uinput.ABS_Y + (0, 255, 0, 0), uinput.ABS_Z + (0, 32768, 0, 0),
#     uinput.ABS_RX,
#     uinput.ABS_HAT0X, uinput.ABS_HAT0Y,
#     uinput.BTN_0, uinput.BTN_1, uinput.BTN_2, uinput.BTN_3, uinput.BTN_4, uinput.BTN_5, uinput.BTN_6, uinput.BTN_7, uinput.BTN_8, uinput.BTN_9)

cap = {
    ecodes.EV_FF:  [ecodes.FF_AUTOCENTER, ecodes.FF_CONSTANT, ecodes.FF_CUSTOM, ecodes.FF_DAMPER, ecodes.FF_EFFECT_MAX, ecodes.FF_EFFECT_MIN, ecodes.FF_FRICTION, ecodes.FF_GAIN, ecodes.FF_INERTIA, ecodes.FF_MAX, ecodes.FF_MAX_EFFECTS, ecodes.FF_PERIODIC, ecodes.FF_RAMP, ecodes.FF_RUMBLE, ecodes.FF_SAW_DOWN, ecodes.FF_SAW_UP, ecodes.FF_SINE, ecodes.FF_SPRING, ecodes.FF_SINE, ecodes.FF_SQUARE],
    ecodes.EV_KEY: [ecodes.KEY_A, ecodes.KEY_B, ecodes.BTN_0, ecodes.BTN_1, ecodes.BTN_2, ecodes.BTN_3, ecodes.BTN_4, ecodes.BTN_5, ecodes.BTN_6, ecodes.BTN_7, ecodes.BTN_8, ecodes.BTN_9],
    ecodes.EV_ABS: [ecodes.ABS_X, ecodes.ABS_Y, ecodes.ABS_RX, ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y,
        (ecodes.ABS_Z, AbsInfo(value=0, min=0, max=0xffff, fuzz=0, flat=0, resolution=0))] # this is the one that we actually care about
}

def map_value(value, in_min, in_max, out_min, out_max):
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min))

running = True

def try_find_config(create_on_missing=True):
    try:
        with open('config.json', 'r') as f:
            return Config.from_json(f.read())
    except FileNotFoundError:
        if not create_on_missing:
            raise
        with open('config.json', 'w+') as f:
            config = Config()
            f.write(config.to_json(indent=4))
            print('Config file config.json not found, writing template config to there')
            return config

def main():
    global running
    print('Starting wheel...')

    import odrive
    odrv0 = odrive.find_any()

    config = try_find_config()
    config_box = ConfigBox(config)

    steering_info = SteeringInfo()

    device = UInput(cap, name='uinput-wheel-ffb', version=0x3)
    time.sleep(1)

    # random events to make steam recognise it as an input device
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

    odrv0 = odrive.find_any()

    odrv0.axis0.controller.config.control_mode = ControlMode.TORQUE_CONTROL
    odrv0.axis0.controller.config.input_mode = InputMode.PASSTHROUGH
    odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL

    t = threading.Thread(target=lambda: input_loop(device, odrv0, config_box, steering_info))
    t.start()

    if config.auto_reread_config:
        t2 = threading.Thread(target=lambda: reread_config_loop(config_box))
        t2.start()
    # threading.Thread(target=ui_debug.main).start()
    # t2 = threading.Thread(target=lambda: receive_ffb_loop(device, odrv0))
    # t2.start()
    # t2.join()

    try:
        receive_ffb_loop(device, odrv0, config_box, steering_info)
    except KeyboardInterrupt:
        device.close()
        running = False
    
def reread_config_loop(config_box: ConfigBox):
    while running:
        config_box.config = try_find_config(create_on_missing=False)
        time.sleep(5)

def input_loop(device, odrv0, config_box: ConfigBox, steering_info: SteeringInfo):
    while running:
        endpoint = config_box.config.total_rotations / 2
        now = time.perf_counter()

        val = map_value(odrv0.axis0.pos_estimate, -endpoint, endpoint, 0, 0xffff)

        steering_info.last_steering = steering_info.steering
        steering_info.last_steering_time = steering_info.steering_time
        steering_info.steering_time = now
        steering_info.steering = val

        device.write(ecodes.EV_ABS, ecodes.ABS_Z, int(val))
        device.write(ecodes.EV_SYN, ecodes.SYN_REPORT, 0)
        time.sleep(0.01)


def receive_ffb_loop(device, odrv0, config_box: ConfigBox, steering_info: SteeringInfo):
    for event in device.read_loop():
        # print(categorize(event))

        # Wait for an EV_ecodes event that will signal us that an
        # effect upload/erase operation is in progress.
        if event.type != ecodes.EV_UINPUT:
            continue

        if event.code == ecodes.UI_FF_UPLOAD:
            upload = device.begin_upload(event.value)
            upload.retval = 0

            const = upload.effect.u.ff_constant_effect
            raw_force = const.level

            device.end_upload(upload)

            # serial_connection.write(bytes(f'{force}\n', 'utf-8'))

            scaled_force = raw_force * config_box.config.sensitivity
            damped_force = scaled_force
            if steering_info.last_steering is not None:
                damped_force += (steering_info.last_steering - steering_info.steering) / (steering_info.steering_time - steering_info.last_steering_time) * config_box.config.damping * 0.0001
            
            if config_box.config.print_ffb_debug:
                print('------------')
                print(f'Raw force: {raw_force}')
                print(f'Scaled force: {scaled_force}')
                print(f'Damped force: {damped_force}')
            

            odrv0.axis0.controller.input_torque = damped_force
            odrv0.axis0.watchdog_feed()

            if odrv0.axis0.current_state != AxisState.CLOSED_LOOP_CONTROL:
                print(odrv0.axis0.disarm_reason)
                if config_box.config.ignore_odrive_errors:
                    odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
                    print("forcing odrive back on")

            # ui_debug.set_val(force)
            time.time()

        elif event.code == ecodes.UI_FF_ERASE:
            erase = device.begin_erase(event.value)
            print(f'[erase] effect_id {erase.effect_id}')

            erase.retval = 0
            device.end_erase(erase)
        
        else:
            print(event.code)

if __name__ == '__main__':
    main()