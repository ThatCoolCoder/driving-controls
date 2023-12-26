from serial import Serial
import uinput
from evdev import UInput, categorize, ecodes
import time
import threading


debug = False
clicks_per_rotation = 80
total_rotations = 3 # from full-left to full-right
inverted = False

events = (uinput.BTN_JOYSTICK,
    uinput.ABS_X + (0, 255, 0, 0), uinput.ABS_Y + (0, 255, 0, 0), uinput.ABS_Z + (0, 32768, 0, 0),
    uinput.ABS_RX,
    uinput.ABS_HAT0X, uinput.ABS_HAT0Y,
    uinput.BTN_0, uinput.BTN_1, uinput.BTN_2, uinput.BTN_3, uinput.BTN_4, uinput.BTN_5, uinput.BTN_6, uinput.BTN_7, uinput.BTN_8, uinput.BTN_9)

cap = {
   ecodes.EV_FF:  [ecodes.FF_AUTOCENTER, ecodes.FF_CONSTANT, ecodes.FF_CUSTOM, ecodes.FF_DAMPER, ecodes.FF_EFFECT_MAX, ecodes.FF_EFFECT_MIN, ecodes.FF_FRICTION, ecodes.FF_GAIN, ecodes.FF_INERTIA, ecodes.FF_MAX, ecodes.FF_MAX_EFFECTS, ecodes.FF_PERIODIC, ecodes.FF_RAMP, ecodes.FF_RUMBLE, ecodes.FF_SAW_DOWN, ecodes.FF_SAW_UP, ecodes.FF_SINE, ecodes.FF_SPRING, ecodes.FF_SINE, ecodes.FF_SQUARE],
   ecodes.EV_KEY: [ecodes.KEY_A, ecodes.KEY_B, ecodes.BTN_0, ecodes.BTN_1, ecodes.BTN_2, ecodes.BTN_3, ecodes.BTN_4, ecodes.BTN_5, ecodes.BTN_6, ecodes.BTN_7, ecodes.BTN_8, ecodes.BTN_9],
   ecodes.EV_ABS: [ecodes.ABS_X, ecodes.ABS_Y, uinput.ABS_Z + (0, 32768, 0, 0), ecodes.ABS_RX, ecodes.ABS_HAT0X, ecodes.ABS_HAT0Y]
}

def map_value(value, in_min, in_max, out_min, out_max):
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min))

def main(serial_path='/dev/ttyACM0'):
    print('Starting wheel...')
    prev_rotations = 0

    device = UInput(cap, name='uinput-wheel-ffb', version=0x3)
    time.sleep(1)

    # random events to make steam recognise it as an input device
    device.emit(uinput.ABS_X, 0, syn=False)
    device.emit(uinput.ABS_Y, 0, syn=False)
    device.emit(uinput.ABS_Z, 0, syn=False)
    device.emit(uinput.ABS_RX, 0, syn=False)
    device.emit(uinput.ABS_HAT0X, 0, True)
    device.emit(uinput.ABS_HAT0Y, 0, True)
    device.emit(uinput.BTN_JOYSTICK, 0, True)
    device.emit(uinput.BTN_0, 0, True)
    device.emit(uinput.BTN_1, 0, True)
    device.emit(uinput.BTN_2, 0, True)
    device.emit(uinput.BTN_3, 0, True)
    device.emit(uinput.BTN_4, 0, True)
    device.emit(uinput.BTN_5, 0, True)
    device.emit(uinput.BTN_6, 0, True)
    device.emit(uinput.BTN_7, 0, True)
    device.emit(uinput.BTN_8, 0, True)
    device.emit(uinput.BTN_9, 0, True)

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
            if debug:
                print(f'Debug data: {data}')
            
            rotations = int(data) / clicks_per_rotation
            rotations = min(total_rotations / 2, max(-total_rotations / 2, rotations))
            if inverted:
                rotations = -rotations
                
            final_value = int(map_value(rotations, -total_rotations / 2, total_rotations / 2, 0, 32768))

            device.write(ecodes.EV_ABS, ecodes.ABS_Z, final_value)
            device.write(ecodes.EV_SYN, ecodes.SYN_REPORT, 0)
        else:
            print(f'Unrecognised data type. Full line: {line}')

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