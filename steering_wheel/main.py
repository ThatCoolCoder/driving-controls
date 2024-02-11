from serial import Serial
import time

from evdev import UInput, ecodes as e, AbsInfo


debug = True
clicks_per_rotation = 360 * 4
total_rotations = 3 # from full-left to full-right
inverted = False

cap = {
    e.EV_KEY : [e.BTN_0, e.BTN_1, e.BTN_2, e.BTN_3, e.BTN_4, e.BTN_5, e.BTN_6, e.BTN_7],
    e.EV_ABS: [
        (e.ABS_X, AbsInfo(value = 0, min = 0, max = 0x7fff, fuzz=0, flat=0, resolution=10)),
        (e.ABS_Y, AbsInfo(value = 0, min = 0, max = 0x7fff, fuzz=0, flat=0, resolution=10)),
        (e.ABS_Z, AbsInfo(value = 0, min = 0, max = 0x7fff, fuzz=0, flat=0, resolution=10)),
    ]
}

def map_value(value, in_min, in_max, out_min, out_max):
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min))

def main(serial_path='/dev/ttyACM0'):
    print('Starting wheel...')

    ui = UInput(cap, name="uinput-wheel")
    time.sleep(1)

    # random events to make steam recognise it as an input device
    ui.write(e.EV_ABS, e.ABS_X, 0)
    ui.write(e.EV_ABS, e.ABS_Y, 0)
    ui.write(e.EV_ABS, e.ABS_Z, 0)

    # ui.write(uinput.ABS_RX, 0, False)
    # ui.write(uinput.ABS_HAT0X, 0, True)
    # ui.write(uinput.ABS_HAT0Y, 0, True)

    ui.write(e.EV_KEY, e.BTN_0, 0)
    ui.write(e.EV_KEY, e.BTN_1, 0)
    ui.write(e.EV_KEY, e.BTN_2, 0)
    ui.write(e.EV_KEY, e.BTN_3, 0)
    ui.write(e.EV_KEY, e.BTN_4, 0)
    ui.write(e.EV_KEY, e.BTN_5, 0)
    ui.write(e.EV_KEY, e.BTN_6, 0)
    ui.write(e.EV_KEY, e.BTN_7, 0)

    with Serial(serial_path, 2000000) as serial_connection:
        while True:
            try:
                line = serial_connection.readline().decode('utf-8').strip()

                if debug:
                    print(f'Debug data: {line}')
                
                use_line(line, ui)
            except Exception:
                print('Error parsing line')
                time.sleep(1) # Avoid spamming terminal
                continue

prev = 0

def use_line(line: str, ui: UInput):
    global prev
    split = line.split(',')
            
    rotations = int(split[0]) / clicks_per_rotation
    rotations = min(total_rotations / 2, max(-total_rotations / 2, rotations))
    if inverted:
        rotations = -rotations
        
    final_value = int(map_value(rotations, -total_rotations / 2, total_rotations / 2, 0, 0x7fff))

    ui.write(e.EV_ABS, e.ABS_Z, final_value)


    print(int(split[1]) == 1)
    ui.write(e.EV_KEY, e.BTN_JOYSTICK, int(split[1]) == 1)
    # prev = int(split[1])
    # device.emit_click(uinput.BTN_1)

if __name__ == '__main__':
    main('/dev/ttyACM0')