#include <Arduino.h>
#include "HX711.h"
#include <Joystick.h>

#define BUZZER 8

// Yes I know loops and arrays exist but there's only 3 of them, it's actually shorter & faster to just copy + paste
HX711 accel;
HX711 brake;
HX711 clutch;

const uint16_t FULL_PRESS_VALUE = 0x7FFF;
const float start_deadzone = -0.03; // negative deadzone means that the range is extended - normally this wouldn't be possible but it works as we have the raw hardware readings
const float end_deadzone = 0.02;

float accel_min;
float accel_max;
float brake_min;
float brake_max;
float clutch_min;
float clutch_max;

Joystick_ joystick(JOYSTICK_DEFAULT_REPORT_ID, JOYSTICK_TYPE_MULTI_AXIS, 0, 0,
	true, true, true, true, true, true, true, true, true, true, true);

void setup()
{
    accel.begin(2, 3);
    brake.begin(4, 5);
    clutch.begin(6, 7);

    pinMode(BUZZER, OUTPUT);

    calibrate();
}

void calibrate()
{
    beep(300);

    accel.tare();
    brake.tare();
    clutch.tare();

    delay(5000);
    brake_max = brake.get_value(10U);
    brake_min = brake_max * start_deadzone;
    brake_max -= brake_max * end_deadzone;

    clutch_max = clutch.get_value(10U);
    clutch_min = clutch_max * start_deadzone;
    clutch_max -= clutch_max * end_deadzone;
    repeated_beep(2);

    delay(2000);
    accel_max = accel.get_value(10U);
    accel_min = accel_max * start_deadzone;
    accel_max -= accel_max * end_deadzone;

    repeated_beep(3);

	joystick.begin();
	joystick.setRxAxisRange(0, FULL_PRESS_VALUE);
	joystick.setRyAxisRange(0, FULL_PRESS_VALUE);
	joystick.setRzAxisRange(0, FULL_PRESS_VALUE);
}

void loop()
{
    float accelValue = map_value(accel.get_value(), accel_min, accel_max, 0, (float) FULL_PRESS_VALUE);
    float brakeValue = map_value(brake.get_value(), brake_min, brake_max, 0, (float) FULL_PRESS_VALUE);
    float clutchValue = map_value(clutch.get_value(), clutch_min, clutch_max, 0, (float) FULL_PRESS_VALUE);

    joystick.setRxAxis(constrain(accelValue, 0, FULL_PRESS_VALUE ));
    joystick.setRyAxis(constrain(brakeValue, 0, FULL_PRESS_VALUE ));
    joystick.setRzAxis(constrain(clutchValue, 0, FULL_PRESS_VALUE ));
}

void beep(int duration)
{

    digitalWrite(BUZZER, HIGH);
    delay(duration);
    digitalWrite(BUZZER, LOW);
}

void repeated_beep(int times)
{
    for (int i = 0; i < times - 1; i ++)
    {
        beep(100);
        delay(100);
    }
    beep(100);
}

float map_value(float value, float in_min, float in_max, float out_min, float out_max)
{
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min));
}

float clamp(float value, float out_min, float out_max)
{
    return min(max(value, out_min), out_max);
}