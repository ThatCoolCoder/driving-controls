#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>
#include <Joystick.h>

// CONFIG

const int clicks_per_rotation = 360 * 4;
const float n_rotations = 3;

#define OUTPUT_RANGE 0x7FFF

Encoders encoder(2,3);

const int n_buttons = 3;
int buttons[n_buttons] = {4, 5, 6};
int buttons_inverted[n_buttons] = {false, false, false};
unsigned long button_debounce_times[n_buttons] = {50, 100, 100}; // in millis

const bool recenter_button_active = true;
const int recenter_button_pin = 7;

// END CONFIG

int last_button_values[n_buttons];
unsigned long buttons_last_changed[n_buttons];

Joystick_ joystick(JOYSTICK_DEFAULT_REPORT_ID, JOYSTICK_TYPE_MULTI_AXIS, n_buttons + (int) recenter_button_active, 0,
	true, true, true, true, true, true, true, true, true, true, true);


void setup()
{
	joystick.begin();
	joystick.setXAxisRange(0, OUTPUT_RANGE);
	for (int i = 0; i < n_buttons; i ++)
	{
		pinMode(buttons[i], INPUT_PULLUP);
		last_button_values[i] = buttons_inverted[i];
		buttons_last_changed[i] = 0;
	}
	if (recenter_button_active) pinMode(recenter_button_pin, INPUT_PULLUP);
}

void loop()
{
	float raw = encoder.getEncoderCount();
	float val = map_value(raw, -clicks_per_rotation * n_rotations / 2.0f, clicks_per_rotation * n_rotations / 2.0f, 0, OUTPUT_RANGE);

	val = min(max(val, 0), OUTPUT_RANGE);

	joystick.setXAxis((int)val);

	for (int i = 0; i < n_buttons; i ++)
	{
		int new_val = (digitalRead(buttons[i]) == LOW) ^ buttons_inverted[i];
		unsigned long now = millis();

		if (new_val != last_button_values[i] && now - buttons_last_changed[i] >= button_debounce_times[i])
		{
			last_button_values[i] = new_val;
			buttons_last_changed[i] = now;
			joystick.setButton(i, new_val);
		}
	}

	if (recenter_button_active && digitalRead(recenter_button_pin) == LOW) encoder.setEncoderCount(0);

	delay(5); // slight delay helps debounce the encoder
}



float map_value(float value, float in_min, float in_max, float out_min, float out_max)
{
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min));
}