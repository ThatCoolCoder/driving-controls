#include <Arduino.h>
#include "HX711.h"

#define BUZZER 8

// Yes I know loops and arrays exist but there's only 3 of them, it's actually shorter & faster to just copy + paste
HX711 accel;
HX711 brake;
HX711 clutch;

const uint16_t FULL_PRESS_VALUE = 0xFFFF;
const float start_deadzone = -0.1; // negative deadzone means that the range is extended - this is possible as we have the raw hardware readings
const float end_deadzone = 0.02;

float accel_min;
float accel_max;
float brake_min;
float brake_max;
float clutch_min;
float clutch_max;

void setup()
{
    Serial.begin(2000000);

    accel.begin(2, 3);
    brake.begin(4, 5);
    clutch.begin(6, 7);

    pinMode(BUZZER, OUTPUT);
    digitalWrite(BUZZER, LOW);
    
    calibrate();
}

void calibrate()
{
    show_message("-- STARTING CALIBRATION --");
    beep(300);

    accel.tare();
    brake.tare();
    clutch.tare();

    show_message("Please press brake and clutch fully for calibration");
    delay(2000);
    brake_max = brake.get_value(10U);
    brake_min = brake_max * start_deadzone;
    brake_max -= brake_max * end_deadzone;
    // clutch_max = clutch.get_value(10U); todo: buy hx711 for clutch
    repeated_beep(2);

    show_message("Please press accelerator fully for calibration");
    delay(2000);
    accel_max = accel.get_value(10U);
    accel_min = accel_max * start_deadzone;
    accel_max -= accel_max * end_deadzone;

    show_message("Calibration complete");
    repeated_beep(3);
}

void loop()
{
    long accelValue = (long) map_value(accel.get_value(), accel_min, accel_max, 0, (float) FULL_PRESS_VALUE);
    long brakeValue = (long) map_value(brake.get_value(), brake_min, brake_max, 0, (float) FULL_PRESS_VALUE);
    int clutchValue = 0; // todo: buy hx711 for clutch
    send_data(String(accelValue) + ',' + String(brakeValue) + ',' + String(clutchValue));
}

void show_message(String message)
{
    Serial.println("text:" + message);
}

void send_data(String data)
{
    Serial.println("data:" + data);
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