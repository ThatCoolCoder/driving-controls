#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

const int CLICKS_PER_REVOLUTION = 360 * 4;

/* Assign a unique ID to this sensor at the same time */
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345);

// Inputs
Encoders encoder(2,3);

bool mag_active = false;
float centered_heading = 0;

void setup()
{
	// Setuzp Serial Monitor
	Serial.begin(2000000);

	/* Initialise the sensor */
	if(mag.begin())
	{
		mag_active = true;

		// Calibrate center
		sensors_event_t event;
		mag.getEvent(&event);
		centered_heading = atan2(event.magnetic.y, event.magnetic.x);
	}
	else show_message("No HMC5883 detected, disabling head tracking");
}


void loop() {
	unsigned long crntTime = millis();

	// send_to_python(encoder.getEncoderCount());
	if (mag_active)
	{
		sensors_event_t event;
		mag.getEvent(&event);
		float heading = atan2(event.magnetic.y, event.magnetic.x);
		float delta = heading - centered_heading;
		send_to_python(delta);
	}

	delay(10);
}

void show_message(String s)
{
    Serial.println("text:" + s);
}

void send_to_python(int i)
{
    send_to_python(String(i));
}

void send_to_python(float f)
{
    send_to_python(String(f));
}

void send_to_python(String s)
{
    Serial.println("data:" + s);
}