from serial import Serial
import uinput
import time

debug = False

# There are uinput events called gas + brake but steam isn't recognising them, so we use regular axes
GAS_EVENT = uinput.ABS_THROTTLE
GAS_LIMITS = (500, 596) # Used to calibrate movement range. Reverse order to invert direction
BRAKE_EVENT = uinput.ABS_X
BRAKE_LIMITS = (450, 413)
CLUTCH_EVENT = uinput.ABS_Y
CLUTCH_LIMITS = (547, 590)

events = (
    GAS_EVENT + (0, 255, 0, 0), BRAKE_EVENT + (0, 255, 0, 0), CLUTCH_EVENT + (0, 255, 0, 0),

    # random stuff to make sure steam recognises it as a controller
    uinput.BTN_JOYSTICK,
    uinput.ABS_X + (0, 255, 0, 0), uinput.ABS_Y + (0, 255, 0, 0), uinput.ABS_Z + (0, 255, 0, 0),
    uinput.ABS_RX,
    uinput.ABS_HAT0X, uinput.ABS_HAT0Y,
    uinput.BTN_0, uinput.BTN_1, uinput.BTN_2, uinput.BTN_3, uinput.BTN_4, uinput.BTN_5, uinput.BTN_6, uinput.BTN_7, uinput.BTN_8, uinput.BTN_9)


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

def map_value(value, in_min, in_max, out_min, out_max):
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min))

def map_to_output(value, limits):
    mapped_value = map_value(value, limits[0], limits[1], 0, 255)
    return int(mapped_value)

with Serial('/dev/ttyACM0', 115200) as serial_connection:
    while True:
        try:
            line = serial_connection.readline().decode('utf-8').strip()

            if debug:
                print(f'Debug data: {line}')

            (gas_value, brake_value, clutch_value) = map(int, line.split(','))
            device.emit(GAS_EVENT, map_to_output(gas_value, GAS_LIMITS))
            device.emit(BRAKE_EVENT, map_to_output(brake_value, BRAKE_LIMITS))
            device.emit(CLUTCH_EVENT, map_to_output(clutch_value, CLUTCH_LIMITS))

        except Exception as e:
            print('Error parsing line')
            time.sleep(1) # Avoid spamming terminal
            if debug:
                print(e)
            else:
                continue