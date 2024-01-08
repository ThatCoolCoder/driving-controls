from serial import Serial
import uinput
import time

debug = False
clicks_per_rotation = 360 * 4
total_rotations = 3 # from full-left to full-right
inverted = False

STEERING_EVENT = uinput.ABS_Z
CAMERA_HEADING_EVENT = uinput.ABS_RY

events = (uinput.BTN_JOYSTICK,
    uinput.ABS_X + (0, 255, 0, 0), uinput.ABS_Y + (0, 255, 0, 0), STEERING_EVENT + (0, 0xFFFF, 0, 0),
    CAMERA_HEADING_EVENT + (0, 0xFFFF, 0, 0),
    
    uinput.ABS_RX,
    uinput.ABS_HAT0X, uinput.ABS_HAT0Y,
    uinput.BTN_0, uinput.BTN_1, uinput.BTN_2, uinput.BTN_3, uinput.BTN_4, uinput.BTN_5, uinput.BTN_6, uinput.BTN_7, uinput.BTN_8, uinput.BTN_9)

def map_value(value, in_min, in_max, out_min, out_max):
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min))

def main(serial_path='/dev/ttyACM0'):
    print('Starting wheel...')

    device = uinput.Device(events, name="uinput-wheel")
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
                

                angle = map_value(float(data), -1, 1, 0, 0xFFFF)
                device.emit(CAMERA_HEADING_EVENT, int(angle))
                continue
                
                rotations = int(data) / clicks_per_rotation
                rotations = min(total_rotations / 2, max(-total_rotations / 2, rotations))
                if inverted:
                    rotations = -rotations
                    
                final_value = int(map_value(rotations, -total_rotations / 2, total_rotations / 2, 0, 0xFFFF))

                device.emit(uinput.ABS_Z, final_value)
            else:
                print(f'Unrecognised data type. Full line: {line}')

if __name__ == '__main__':
    main('/dev/ttyACM0')