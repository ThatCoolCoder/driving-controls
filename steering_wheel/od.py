import odrive
from odrive.utils import dump_errors
from odrive.enums import *
from time import sleep
from math import sin

odrv0 = odrive.find_any()

odrv0.axis0.controller.config.control_mode = ControlMode.TORQUE_CONTROL
odrv0.axis0.controller.config.input_mode = InputMode.PASSTHROUGH
# odrv0.axis0.controller.config.control_mode = ControlMode.POSITION_CONTROL
# odrv0.axis0.controller.config.input_mode = InputMode.POS_FILTER
odrv0.axis0.config.motor.torque_constant = 8.23 / 8
odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL


print(list(ODriveError))

t = 0
while True:
    # odrv0.axis0.controller.input_pos = sin(t) * 0.1
    odrv0.axis0.controller.input_torque = sin(t * 25) * 5
    sleep(0.01)
    print(dump_errors(odrv0))
    t += 0.01