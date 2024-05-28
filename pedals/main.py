from serial import Serial
import uinput
import time

# CONFIG START

debug = False

# There are uinput events called gas + brake but steam isn't recognising them, so we use regular axes
GAS_EVENT = uinput.ABS_THROTTLE
BRAKE_EVENT = uinput.ABS_X
CLUTCH_EVENT = uinput.ABS_Y

# CONFIG END

events = (
    GAS_EVENT + (0, 0xFFFF, 0, 0), BRAKE_EVENT + (0, 0xFFFF, 0, 0), CLUTCH_EVENT + (0, 0xFFFF, 0, 0),

    # random stuff to make sure steam recognises it as a controller
    uinput.BTN_JOYSTICK,
    uinput.ABS_RX,
    uinput.ABS_HAT0X, uinput.ABS_HAT0Y,
    uinput.BTN_0, uinput.BTN_1, uinput.BTN_2, uinput.BTN_3, uinput.BTN_4, uinput.BTN_5, uinput.BTN_6, uinput.BTN_7, uinput.BTN_8, uinput.BTN_9)

def main(serial_path='/dev/ttyACM0'):
    print('Starting pedals...')
    device = uinput.Device(events, name="uinupt-pedals")
    time.sleep(1)

    device.emit(GAS_EVENT, 0)
    device.emit(BRAKE_EVENT, 255)
    device.emit(CLUTCH_EVENT, 255)

    # random stuff to make sure steam recognises it as a controller
    device.emit(uinput.ABS_X, 128, syn=False)
    device.emit(uinput.ABS_Y, 128, syn=False)
    device.emit(uinput.ABS_Z, 128, syn=False)
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

                if debug:
                    print(f'Debug data: {line}')

                split_data = line.split(':', 1)
                if len(split_data) < 2:
                    print(f'Line isn\'t in expected format (no colon): {line}')
                    continue

                (prefix, data) = split_data

                if prefix == 'text':
                    print(data)
                elif prefix == 'data':
                    handle_data(data, device)
                else:
                    print(f'Unexpected data label: {prefix}')

            except Exception as e:
                print('Error parsing line')
                time.sleep(1) # Avoid spamming terminal
                if debug:
                    print(e)
                else:
                    continue

def handle_data(data, device):
    (gas_value, brake_value, clutch_value) = map(float, data.split(','))

    device.emit(GAS_EVENT, map_to_output(gas_value))
    device.emit(BRAKE_EVENT, map_to_output(brake_value))
    device.emit(CLUTCH_EVENT, map_to_output(clutch_value))

def map_to_output(value):
    return int(min(max(value, 0), 0xFFFF))

if __name__ == '__main__':
    main()
