#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>

// Inputs
Encoders encoder(2,3);

const int CLICKS_PER_REVOLUTION = 360 * 4;

void setup()
{
	// Setuzp Serial Monitor
	Serial.begin(2000000);
}


void loop() {
	unsigned long crntTime = millis();

	send_to_python(encoder.getEncoderCount());
	delay(10);
}

void send_to_python(String s)
{
    Serial.println("text:" + s);
}

void send_to_python(int i)
{
    Serial.print("data:");
    Serial.println(i);
}