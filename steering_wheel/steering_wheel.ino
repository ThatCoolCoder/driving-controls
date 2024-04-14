#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>
#include <Joystick.h>

#define OUTPUT_RANGE 0x7FFF

Encoders encoder(2,3);

const int n_buttons = 3;
int buttons[n_buttons] = {4, 5, 6};
int buttons_inverted[n_buttons] = {false, true, true};

const int clicks_per_rotation = 360 * 4;
const float n_rotations = 3;

Joystick_ joystick(JOYSTICK_DEFAULT_REPORT_ID, JOYSTICK_TYPE_MULTI_AXIS, max(n_buttons, 8), 0,
	true, true, true, true, true, true, true, true, true, true, true);


void setup()
{
	joystick.begin();
	joystick.setXAxisRange(0, OUTPUT_RANGE);
	for (int i = 0; i < n_buttons; i ++) pinMode(buttons[i], INPUT_PULLUP);

}

void loop()
{
	float raw = encoder.getEncoderCount();
	float val = map_value(raw, -clicks_per_rotation * n_rotations / 2.0f, clicks_per_rotation * n_rotations / 2.0f, 0, OUTPUT_RANGE);

	val = min(max(val, 0), OUTPUT_RANGE);

	joystick.setXAxis((int)val);

	for (int i = 0; i < n_buttons; i ++)
	{
		joystick.setButton(i, (digitalRead(buttons[i]) == LOW) ^ buttons_inverted[i]);
	}

	delay(10);
}



float map_value(float value, float in_min, float in_max, float out_min, float out_max)
{
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min));
}