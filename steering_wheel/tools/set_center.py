import odrive
from fibre.libfibre import ObjectLostError

if __name__ == '__main__':
    odrv0 = odrive.find_any(timeout=10)

    input('Rotate wheel to centered position and press enter to save this as the new centerpoint. Press ctrl+c to cancel')

    print('Applying changes...')
    odrv0.axis0.controller.config.absolute_setpoints = True
    odrv0.axis0.pos_vel_mapper.config.offset = (odrv0.axis0.pos_vel_mapper.config.offset - odrv0.axis0.pos_estimate) % 1
    odrv0.axis0.pos_vel_mapper.config.offset_valid = True
    odrv0.axis0.pos_vel_mapper.config.approx_init_pos = 0.0
    odrv0.axis0.pos_vel_mapper.config.approx_init_pos_valid = True
    try:
        odrv0.save_configuration()
    except ObjectLostError:
        pass

    print('Complete')