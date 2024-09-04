from serial import Serial
import time
from evdev import UInput, categorize, ecodes
import asyncio
import json
import threading

debug = False
clicks_per_rotation = 20
total_rotations = 3 # from full-left to full-right
inverted = True

cap = {
   ecodes.EV_FF:  [ecodes.FF_AUTOCENTER, ecodes.FF_CONSTANT, ecodes.FF_CUSTOM, ecodes.FF_DAMPER, ecodes.FF_EFFECT_MAX, ecodes.FF_EFFECT_MIN, ecodes.FF_FRICTION, ecodes.FF_GAIN, ecodes.FF_INERTIA, ecodes.FF_MAX, ecodes.FF_MAX_EFFECTS, ecodes.FF_PERIODIC, ecodes.FF_RAMP, ecodes.FF_RUMBLE, ecodes.FF_SAW_DOWN, ecodes.FF_SAW_UP, ecodes.FF_SINE, ecodes.FF_SPRING, ecodes.FF_SINE, ecodes.FF_SQUARE],
   ecodes.EV_KEY: [ecodes.KEY_A, ecodes.KEY_B, ecodes.BTN_0, ecodes.BTN_1, ecodes.BTN_2, ecodes.BTN_3, ecodes.BTN_4, ecodes.BTN_5, ecodes.BTN_6, ecodes.BTN_7, ecodes.BTN_8, ecodes.BTN_9],
   ecodes.EV_ABS: [ecodes.ABS_X, ecodes.ABS_Y, ecodes.ABS_Z, ecodes.ABS_RX, ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y]
}

def map_value(value, in_min, in_max, out_min, out_max):
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min))

def main(serial_path):
    print('Starting wheel...')

    device = UInput(cap, name='ffbtestwheel', version=0x3)
    time.sleep(1)

    device.write(ecodes.EV_ABS, ecodes.ABS_X, 128)
    device.write(ecodes.EV_ABS, ecodes.ABS_Y, 128)
    device.write(ecodes.EV_ABS, ecodes.ABS_Z, 128)
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

    with Serial(serial_path, 2000000) as serial_connection:
        t = threading.Thread(target=lambda: input_loop(serial_connection, device))
        t.start()
        threading.Thread(target=lambda: receive_ffb_loop(serial_connection, device)).start()
        t.join()
            
def input_loop(serial_connection, device):
    while True:
        try:
            line = serial_connection.readline().decode('utf-8').strip()
        except Exception:
            print('Error parsing line')
            time.sleep(1) # Avoid spamming terminal
            continue
        
        split_data = line.split(':', 1)
        if len(split_data) < 2:
            print(f'Line isn\'t in expected format (no colon): {line}')
            continue

        (prefix, data) = split_data
        if prefix == 'text':
            print(f'Text: {data}')
        elif prefix == 'data':
            rotations = (int(data) + 1) / clicks_per_rotation
            rotations = min(total_rotations / 2, max(-total_rotations / 2, rotations))
            if inverted:
                rotations = -rotations
                
            final_value = int(map_value(rotations, -total_rotations / 2, total_rotations / 2, -32768, 32768))

            device.write(ecodes.EV_ABS, ecodes.ABS_X, final_value)
            device.write(ecodes.EV_SYN, ecodes.SYN_REPORT, 0)
        else:
            print(f'Unrecognised data type. Full line: {line}', flush=True)

def receive_ffb_loop(serial_connection, device):
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

            serial_connection.write(bytes(f'{force}\n', 'utf-8'))

        elif event.code == ecodes.UI_FF_ERASE:
            erase = device.begin_erase(event.value)
            print(f'[erase] effect_id {erase.effect_id}')

            erase.retval = 0
            device.end_erase(erase)

if __name__ == '__main__':
    main('/dev/ttyACM0')
