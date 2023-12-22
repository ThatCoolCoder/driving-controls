#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>

// Inputs
Encoders encoder(2,3);
#define STRAIGHT_SWITCH 5 // a switch that goes LOW only when the wheel is straight (not necessarily centered, just vertical). Compensates for encoder drift.


// Try and prevent it writing too much to serial and having the output drift because it misses clicks
unsigned long last_sent_time = 0;
unsigned long last_was_straight = 0;
unsigned const long MIN_SEND_INTERVAL = 50;
unsigned const long MIN_CHECK_STRAIGHT_INTERVAL = 100; // todo: does this even need to exist? do any issues occur with constant polling?

const int CLICKS_PER_REVOLUTION = 80;
const int STRAIGHT_SWITCH_OFFSET = 1;


void setup()
{
	pinMode(STRAIGHT_SWITCH, INPUT_PULLUP);

	// Setup Serial Monitor
	Serial.begin(2000000);
}


void loop() {
	unsigned long crntTime = millis();

	// Round value to nearest whole revolution when straight
	if ((crntTime - last_was_straight) > MIN_CHECK_STRAIGHT_INTERVAL
		&& digitalRead(STRAIGHT_SWITCH) == LOW) 
    {
		noInterrupts(); // nointerrupts as there are possible race conditions here

        encoder.setEncoderCount(round_n(encoder.getEncoderCount(), CLICKS_PER_REVOLUTION) + STRAIGHT_SWITCH_OFFSET);
		last_was_straight = crntTime;

		interrupts();
    }

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

int round_n (int value, int interval)
{
    // Like normal round but can go to any interval. Works sensibly for negative numbers.
    return value >= 0 ? (value+(interval/2))/interval*interval : (value-(interval/2))/interval*interval ;
}