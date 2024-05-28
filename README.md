# Driving Controls

Code for my Arduino-based DIY wheel and pedals. It's not the best code but it gets the job done. It's not designed to be very configurable; if you want to use it you'll have to go changing things directly in the code. I've mainly put it on Github for backup purposes (but make an issue if you want to chat about this)

Sorry, Linux only.

On this branch I'm currently developing a version with FFB.

## Basic architecture

Pedals:
As I only had an Arduino Uno when first making the wheel, I couldn't directly make it work as a USB device, so it instead just dumps the data to a serial, where a python program reads this and sends it to a virtual UInput device, which is then picked up in game.

There's code for adding a bunch of unused uinput buttons/axes as the controller wouldn't show up in BeamNG running through proton.

Wheel:
Previously it also used an uno but i upgraded to a leonardo to try and improve latency and in preparation for making it ffb.

## arduino libraries to install
- hx711 (by Rob Tillaart)
- enableinterrupt (by Mike Schwager)
- quadratureencoder (by Cheng Saetern)
- [sgtnoodle's fork of the arduino joystick with ffb library](https://github.com/sgtnoodle/ArduinoJoystickWithFFBLibrary) (not on arduino library manager, need to manually install)