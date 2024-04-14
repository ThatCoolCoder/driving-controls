# hacky thing to make pedals function sorta like rudder pedals, since the rudder axis on my joystick has died

from serial import Serial
import uinput
import time

debug = False

# There are uinput events called gas + brake but steam isn't recognising them, so we use regular axes

OUTPUT_EVENT = uinput.ABS_RUDDER

events = (
    OUTPUT_EVENT + (0, 0xFFFF, 0, 0),

    # random stuff to make sure system recognises it as a controller
    uinput.BTN_JOYSTICK,
    uinput.ABS_RX,
    uinput.ABS_HAT0X, uinput.ABS_HAT0Y,
    uinput.BTN_0, uinput.BTN_1, uinput.BTN_2, uinput.BTN_3, uinput.BTN_4, uinput.BTN_5, uinput.BTN_6, uinput.BTN_7, uinput.BTN_8, uinput.BTN_9
)

def main(serial_path='/dev/ttyACM0'):
    print('Starting pedals...')
    device = uinput.Device(events, name="uinupt-rudder-pedals")
    time.sleep(1)

    device.emit(OUTPUT_EVENT, 0)

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
    (gas_value, _, clutch_value) = map(float, data.split(','))

    value = 0x7FFF + gas_value / 2 - clutch_value / 2

    device.emit(OUTPUT_EVENT, map_to_output(value))

def map_to_output(value):
    return int(min(max(value, 0), 0xFFFF))

if __name__ == '__main__':
    main()
