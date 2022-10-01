#include <Arduino.h>

const int num_pins = 3;
const int pins[num_pins] = { A0, A1, A2 }; // in order of accel, brake, clutch
int last_sent_values[num_pins];
const int interval = 10; // main loop interval
const int min_delta = 1; // don't send new data unless it's this different from previous values
unsigned long last_sent_time = 0;
const unsigned long max_send_interval = 500;

void setup()
{
    Serial.begin(115200);
}

void loop()
{
    int new_values[num_pins];
    int biggest_delta = 0;
    for (int i = 0; i < num_pins; i ++)
    {
        int new_value = analogRead(pins[i]);
        new_values[i] = new_value;
        int delta = abs(last_sent_values[i] - new_value);
        biggest_delta = max(biggest_delta, delta);
    }

    unsigned long time = millis();

    if (biggest_delta >= min_delta || abs(time - last_sent_time) > max_send_interval)
    {
        String result = "";
        for (int i = 0; i < num_pins; i ++)
        {
            result += new_values[i];
            if (i != num_pins - 1) result += ",";
            last_sent_values[i] = new_values[i];
        }
        last_sent_time = time;
        Serial.println(result);
    }


    delay(interval);
}