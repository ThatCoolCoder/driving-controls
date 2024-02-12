#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>

Encoders encoder(2,3);

int buttons[] = {4, 5, 6};
const int n_buttons = 3;

void setup()
{
	Serial.begin(2000000);

	for (int i = 0; i < n_buttons; i ++) pinMode(buttons[i], INPUT_PULLUP);
}


void loop()
{
	Serial.print(encoder.getEncoderCount());

	for (int i = 0; i < n_buttons; i ++)
	{
		Serial.print(",");
		Serial.print(digitalRead(buttons[i]) == HIGH);
	}
	Serial.print("\n");
	delay(10);
}