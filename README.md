# Driving Controls

Code for my Arduino-based DIY wheel and pedals. It's not the best code but it gets the job done. It's not designed to be very configurable; if you want to use it you'll have to go changing things directly in the code. I've mainly put it on Github for backup purposes.

Sorry, Linux only.

## Basic architecture

As I only had an Arduino Uno when first making the wheel, I couldn't directly make it work as a USB device, so it instead just dumps the data to a serial, where a python program reads this and sends it to a virtual UInput device, which is then picked up in game. I could have switched over to a Leonardo when buying a second arduino for the pedals but this method worked and I didn't want to change anythign. Perhaps it would give slightly lower latency but I'm happy enough as it is. Perhaps upon trying to make FFB work I'll find the round-trip latency is not ok and I'll change it.

There's code for adding a bunch of unused uinput channels as the controller wouldn't show up in BeamNG running through proton.

## arduino libraries to install
- hx711 (by Rob Tillaart)
- enableinterrupt (by Mike Schwager)
- quadratureencoder (by Cheng Saetern)
- [https://github.com/MHeironimus/ArduinoJoystickLibrary/](https://github.com/MHeironimus/ArduinoJoystickLibrary/) (needs to be manually downloaded and installed - see instructions on that page)