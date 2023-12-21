#include <Arduino.h>
#include <math.h>

// Rotary Encoder Inputs
#define CLK 2
#define DT 3
#define SW 4
#define STRAIGHT_SWITCH 5 // a switch that goes LOW only when the wheel is straight (not centered, just vertical). Compensates for encoder drift

int counter = 0;
int last_state_clk;
unsigned long last_was_straight = 0;
unsigned const long min_check_straight_interval = 1000;

// Try and prevent it writing too much to serial and having the output drift because it misses clicks
unsigned long last_sent_time = 0;
unsigned const long MIN_SEND_INTERVAL = 50;

const int CLICKS_PER_REVOLUTION = 20;
const int STRAIGHT_SWITCH_OFFSET = -1;

void setup()
{
	
	// Set encoder pins as inputs
	pinMode(CLK, INPUT_PULLUP);
	pinMode(DT, INPUT_PULLUP);
	pinMode(SW, INPUT_PULLUP);
	pinMode(LED_BUILTIN, OUTPUT);
	pinMode(STRAIGHT_SWITCH, INPUT_PULLUP);

	// Setup Serial Monitor
	Serial.begin(2000000);

	// Read the initial state of CLK
	last_state_clk = digitalRead(CLK);
}

void loop()
{
    int old_counter = counter;
    update_reading();
	unsigned long time = millis();
    if ((time - last_was_straight) > min_check_straight_interval
		&& digitalRead(STRAIGHT_SWITCH) == LOW) 
    {
        counter = round_n(counter, CLICKS_PER_REVOLUTION) + STRAIGHT_SWITCH_OFFSET;
		last_was_straight = time;
    }

	// digitalWrite(LED_BUILTIN, digitalRead(STRAIGHT_SWITCH));

    if (counter != old_counter && (time - last_sent_time) > MIN_SEND_INTERVAL)
    {
        send_to_python(counter);
		last_sent_time = time;
    }

	// Put in a slight delay to help debounce the reading
	delay(1);
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


void update_reading()
{
	// Read the current state of CLK
	int current_state_clk = digitalRead(CLK);

	// If last and current state of CLK are different, then pulse occurred
	// React to only 1 state change to avoid double count
	if (current_state_clk != last_state_clk  && current_state_clk == 1){

		// If the DT state is different than the CLK state then
		// the encoder is rotating CCW so decrement
		if (digitalRead(DT) != current_state_clk) {
			counter --;
		} else {
			// Encoder is rotating CW so increment
			counter ++;
		}
	}

	// Remember last CLK state
	last_state_clk = current_state_clk;

	// Read the button state
	int btnState = digitalRead(SW);
}

int round_n (int value, int interval)
{
    // Like normal round but can go to any interval. Works sensibly for negative numbers.
    return value >= 0 ? (value+(interval/2))/interval*interval : (value-(interval/2))/interval*interval ;
}