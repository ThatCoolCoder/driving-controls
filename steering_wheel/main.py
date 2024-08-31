from evdev import UInput, categorize, ecodes, AbsInfo
import odrive
from odrive.enums import *
import time
import math
import threading

import ui_debug

debug = False
clicks_per_rotation = 80
total_rotations = 3 # from full-left to full-right
inverted = False

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

def main():
    global running
    print('Starting wheel...')

    import odrive
    odrv0 = odrive.find_any()

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

    t = threading.Thread(target=lambda: input_loop(device, odrv0))
    t.start()
    # threading.Thread(target=ui_debug.main).start()
    # t2 = threading.Thread(target=lambda: receive_ffb_loop(device, odrv0))
    # t2.start()
    # t2.join()

    try:
        receive_ffb_loop(device, odrv0)
    except KeyboardInterrupt:
        device.close()
        running = False

def input_loop(device, odrv0):
    while running:
        val = map_value(odrv0.axis0.pos_estimate, -1.5, 1.5, 0, 0xffff)
        device.write(ecodes.EV_ABS, ecodes.ABS_Z, int(val))
        device.write(ecodes.EV_SYN, ecodes.SYN_REPORT, 0)
        time.sleep(0.01)

def receive_ffb_loop(device, odrv0):
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
            force = const.level

            device.end_upload(upload)

            # serial_connection.write(bytes(f'{force}\n', 'utf-8'))
            odrv0.axis0.controller.input_torque = force / 10
            odrv0.axis0.watchdog_feed()
            print(force)
            if odrv0.axis0.current_state != AxisState.CLOSED_LOOP_CONTROL:
                odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL
                print(odrv0.axis0.disarm_reason)
                print("forcing odrive back on")

            # ui_debug.set_val(force)

        elif event.code == ecodes.UI_FF_ERASE:
            erase = device.begin_erase(event.value)
            print(f'[erase] effect_id {erase.effect_id}')

            erase.retval = 0
            device.end_erase(erase)

if __name__ == '__main__':
    main()