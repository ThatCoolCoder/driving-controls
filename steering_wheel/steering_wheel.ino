#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>

// Inputs
Encoders encoder(2,3);


// Try and prevent it writing too much to serial and having the output drift because it misses clicks
unsigned long last_sent_time = 0;
unsigned const long MIN_SEND_INTERVAL = 50;

const int CLICKS_PER_REVOLUTION = 80;


void setup()
{
	// Setuzp Serial Monitor
	Serial.begin(2000000);
}


void loop() {
	unsigned long crntTime = millis();

	// Send data periodically
	if (crntTime - last_sent_time > MIN_SEND_INTERVAL){ 
		send_to_python(encoder.getEncoderCount());
		
		last_sent_time = crntTime;
	}
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