#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>

// Inputs
Encoders encoder(2,3);

void setup()
{
	// Setup Serial Monitor
	Serial.begin(2000000);
}


void loop() {
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