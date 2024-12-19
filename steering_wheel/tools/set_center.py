import odrive
from odrive.enums import AxisState
from fibre.libfibre import ObjectLostError

def is_nan(val):
    return val != val

def zero_if_nan(val):
    return 0 if is_nan(val) else val

if __name__ == '__main__':
    odrv0 = odrive.find_any(timeout=10)
    odrv0.axis0.requested_state = AxisState.IDLE

    input('Rotate wheel to centered position and press enter to save this as the new centerpoint. Press ctrl+c to cancel')

    print('Applying changes...')
    # if there is a previous messed up config, clear it and say to try again
    if is_nan(odrv0.axis0.pos_estimate):
        print('Invalid existing centerpoint is preventing calibration')

        odrv0.axis0.pos_vel_mapper.config.offset = 0
        odrv0.axis0.pos_vel_mapper.config.offset_valid = True
        odrv0.axis0.pos_vel_mapper.config.approx_init_pos = 0.0
        odrv0.axis0.pos_vel_mapper.config.approx_init_pos_valid = True
        odrv0.axis0.controller.config.absolute_setpoints = True

        try:
            odrv0.save_configuration()
        except ObjectLostError:
            pass
        
        print('Invalid centerpoint has been cleared, please run the program again to set new centerpoint')
        quit()

    odrv0.axis0.pos_vel_mapper.config.offset = (zero_if_nan(odrv0.axis0.pos_vel_mapper.config.offset) - odrv0.axis0.pos_estimate) % 1
    odrv0.axis0.pos_vel_mapper.config.offset_valid = True
    odrv0.axis0.pos_vel_mapper.config.approx_init_pos = 0.0
    odrv0.axis0.pos_vel_mapper.config.approx_init_pos_valid = True
    odrv0.axis0.controller.config.absolute_setpoints = True
    try:
        odrv0.save_configuration()
    except ObjectLostError:
        pass

    print('Complete')