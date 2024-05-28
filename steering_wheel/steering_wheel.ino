#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>
#include <Joystick.h>

// CONFIG

const int clicks_per_rotation = 360 * 4;
const float n_rotations = 3;

#define OUTPUT_RANGE 0x7FFF

Encoders encoder(2,3);

const int n_buttons = 8;
int buttons[n_buttons] = {
	4, 5, 6, 8,
	9, 10, 11, 12
};
int buttons_inverted[n_buttons] = {
	false, false, false, false,
	false, false, false, false
};
unsigned long button_debounce_times[n_buttons] = {
	50, 100, 100, 50,
	50, 50, 50, 50
}; // in millis

const bool recenter_button_active = true;
const int recenter_button_pin = 7;

// END CONFIG

// random joystick stuff

Gains gains[2];
EffectParams effect_params[2];

// end random joystick stuff


int last_button_values[n_buttons];
unsigned long buttons_last_changed[n_buttons];

Joystick_ joystick(JOYSTICK_DEFAULT_REPORT_ID,
	JOYSTICK_TYPE_MULTI_AXIS, n_buttons, 0,
	false, false, false, false, false, false,
	false, false, true, true, true);


void setup()
{
	joystick.begin();
	joystick.setSteeringRange(0, OUTPUT_RANGE);
	for (int i = 0; i < n_buttons; i ++)
	{
		pinMode(buttons[i], INPUT_PULLUP);
		last_button_values[i] = buttons_inverted[i];
		buttons_last_changed[i] = 0;
	}
	if (recenter_button_active) pinMode(recenter_button_pin, INPUT_PULLUP);
	pinMode(13, OUTPUT);

	//set X Axis gains
	gains[0].totalGain = 50;
	gains[0].springGain = 0;

	//set Y Axis gains
	gains[1].totalGain = 50;
	gains[1].springGain = 0;
	joystick.setGains(gains);

	effect_params[0].springMaxPosition = 0;
	effect_params[0].springPosition = 0;
	joystick.setEffectParams(effect_params);
}

void loop()
{
	float raw = encoder.getEncoderCount();
	float val = map_value(raw, -clicks_per_rotation * n_rotations / 2.0f, clicks_per_rotation * n_rotations / 2.0f, 0, OUTPUT_RANGE);

	val = min(max(val, 0), OUTPUT_RANGE);

	joystick.setSteering((int)val);

	if (recenter_button_active && digitalRead(recenter_button_pin) == LOW) encoder.setEncoderCount(0);


	int32_t forces[2] = {0};
	joystick.getForce(forces);
	if (forces[0] > 0) digitalWrite(13, HIGH);
	else digitalWrite(13, LOW);
}



float map_value(float value, float in_min, float in_max, float out_min, float out_max)
{
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min));
}