#include <Arduino.h>
#include "HX711.h"

// Yes I know loops and arrays exist but there's only 3 of them, it's actually shorter & faster to just copy + paste
HX711 accel;
HX711 brake;
HX711 clutch;

const uint16_t FULL_PRESS_VALUE = 0xFFFF;

void setup()
{
    Serial.begin(2000000);

    accel.begin(2, 3);
    brake.begin(4, 5);
    clutch.begin(6, 7);
    
    calibrate();
}

void calibrate()
{
    accel.tare();
    brake.tare();
    clutch.tare();

    show_message("Please press brake and clutch fully for calibration");
    delay(2000);
    brake.calibrate_scale(FULL_PRESS_VALUE);
    clutch.calibrate_scale(FULL_PRESS_VALUE);

    show_message("Please press accelerator fully for calibration");
    delay(2000);
    accel.calibrate_scale(FULL_PRESS_VALUE);

    show_message("Calibration complete");
}

void loop()
{
    float _accelValue = accel.read();
    send_data(String(_accelValue));

    // Probable working:
    int accelValue = (int) accel.read();
    int brakeValue = (int) brake.read();
    int clutchValue = (int) clutch.read();
    // send_data(String(accelValue) + ',' + String(brakeValue) + ',' + String(clutchValue));


    // delay(interval);
}

void show_message(String message)
{
    Serial.println("text:" + message);
}

void send_data(String data)
{
    Serial.println("data:" + data);
}