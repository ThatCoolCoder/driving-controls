# Driving Controls

Code for my DIY sim wheel and pedals. It's not the best code but it gets the job done. It's not designed to be very configurable; if you want to use it you'll have to go changing things directly in the code. I've mainly put it on Github for backup purposes.

Only works on Linux.

## Architecture

### Wheel

The wheel is built from a hoverboard motor (direct drive) and controlled by an odrive s1, this is actually the only microprocessor used. The inbuilt hall encoder on the s1 is used. There is a python program that communicates with the odrive. It uses an evdev virtual device to receive ffb events and send the rotation info back. This appears to have acceptable latency when playing games natively (proton is worse but still decent).

The wheel has code for adding a bunch of unused uinput channels as the controller otherwise wouldn't show up in BeamNG running through proton.

#### Installation notes

In addition to installing from `steering_wheel/requirements.txt`, you will also need to install python-evdev from your system package manager (it is not on pypi).

### Pedals

All three pedals are load-cell, they are connected to the computer through an Arduino Leonardo. As some games do not differentiate between different input devices, the wheel and pedals do not share any axes.

## arduino libraries to install for pedals
- hx711 (by Rob Tillaart)
- enableinterrupt (by Mike Schwager)
- quadratureencoder (by Cheng Saetern)
- [https://github.com/MHeironimus/ArduinoJoystickLibrary/](https://github.com/MHeironimus/ArduinoJoystickLibrary/) (needs to be manually downloaded and installed - see instructions on that page)