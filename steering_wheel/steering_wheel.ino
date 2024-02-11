#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>

#define DOWNSHIFT_HI 8
#define DOWNSHIFT_IN 9

// Inputs
Encoders encoder(2,3);

void setup()
{
	// Setup Serial Monitor
	Serial.begin(2000000);

	pinMode(DOWNSHIFT_HI, OUTPUT);
	digitalWrite(DOWNSHIFT_HI, LOW);
	pinMode(DOWNSHIFT_IN, INPUT_PULLUP);
}


void loop() {
	Serial.println(String(encoder.getEncoderCount()) + "," + String(digitalRead(DOWNSHIFT_IN) == HIGH) + "," + "0");
	delay(10);
}