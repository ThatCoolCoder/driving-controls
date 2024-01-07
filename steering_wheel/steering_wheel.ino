#include <Arduino.h>
#include <math.h>
#include <QuadratureEncoder.h>

#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_HMC5883_U.h>

/* Assign a unique ID to this sensor at the same time */
Adafruit_HMC5883_Unified mag = Adafruit_HMC5883_Unified(12345);

// Inputs
Encoders encoder(2,3);

const int CLICKS_PER_REVOLUTION = 360 * 4;

void setup()
{
	// Setuzp Serial Monitor
	Serial.begin(2000000);

	sensor_t sensor;
	mag.getSensor(&sensor);
	Serial.println("------------------------------------");
	Serial.print  ("Sensor:       "); Serial.println(sensor.name);
	Serial.print  ("Driver Ver:   "); Serial.println(sensor.version);
	Serial.print  ("Unique ID:    "); Serial.println(sensor.sensor_id);
	Serial.print  ("Max Value:    "); Serial.print(sensor.max_value); Serial.println(" uT");
	Serial.print  ("Min Value:    "); Serial.print(sensor.min_value); Serial.println(" uT");
	Serial.print  ("Resolution:   "); Serial.print(sensor.resolution); Serial.println(" uT");  
	Serial.println("------------------------------------");
	Serial.println("");
}


void loop() {
	unsigned long crntTime = millis();

	// send_to_python(encoder.getEncoderCount());
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