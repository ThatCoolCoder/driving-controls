#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>
#include <Joystick.h>

Encoders encoder(2,3);

const int n_buttons = 3;
int buttons[n_buttons] = {4, 5, 6};

const int clicks_per_rotation = 360 * 4;
const float n_rotations = 3;

Joystick_ joystick;


void setup()
{
	// Serial.begin(2000000);

	joystick.begin();
	joystick.setXAxisRange(0, 0XFFFF);
	for (int i = 0; i < n_buttons; i ++) pinMode(buttons[i], INPUT_PULLUP);

}

void loop()
{
	float raw = encoder.getEncoderCount();
	float val = map_value(raw, -clicks_per_rotation * n_rotations / 2.0f, clicks_per_rotation * n_rotations / 2.0f, 0, 0XFFFF);

	joystick.setXAxis((int)val);

	// for (int i = 0; i < n_buttons; i ++)
	// {
	// 	Serial.print(",");
	// 	Serial.print(digitalRead(buttons[i]) == HIGH);
	// }

	delay(10);
}



float map_value(float value, float in_min, float in_max, float out_min, float out_max)
{
    return out_min + (((value - in_min) / (in_max - in_min)) * (out_max - out_min));
}