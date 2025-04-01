# Driving Controls

Code for my DIY force-feedback steering wheel and pedals. This project is made public as a demonstration of how such a wheel could be implemented, rather than being a ready-to-use solution. It is linux-only due to the use of evdev.

## Architecture

### Wheel

The wheel is built from a hoverboard motor (direct drive) and controlled by an odrive s1, this is actually the only microprocessor used. The inbuilt hall encoder on the s1 is used. There is a python program that communicates with the odrive. It uses an evdev virtual device to receive ffb events and send the rotation info back. This appears to have acceptable latency when playing games natively (proton is worse but still decent).

The wheel has code for adding a bunch of unused uinput channels as the controller otherwise wouldn't show up in BeamNG running through proton.

#### Installation & usage

Setup motor/odrive/psu to work correctly in torque control mode. Use pip to install dependencies from `steering_wheel/requirements.txt` (it is recommended to use a venv).

Then run as a module: `python -m steering_wheel`. By default it will launch a web ui for configuring it, run with the `--help` flag to see all options.

### Pedals

All three pedals are load-cell, they are connected to the computer through an Arduino Leonardo. As some games do not differentiate between different input devices, the wheel and pedals do not share any axes.

#### Usage

Upload code onto arduino and plug in.

There is also some legacy python code that allowed the pedals to work with a regular arduino Uno communicating via serial, in future I may clean this up and add it as an option for those who do not have a leonardo.

## arduino libraries to install for pedals
- hx711 (by Rob Tillaart)
- enableinterrupt (by Mike Schwager)
- [https://github.com/MHeironimus/ArduinoJoystickLibrary/](https://github.com/MHeironimus/ArduinoJoystickLibrary/) (needs to be manually downloaded and installed - see instructions on that page)
