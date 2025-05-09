#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVO_FREQ 50
#define MIN_PULSE 0 // 0.5ms (common servo min)
#define MAX_PULSE 500 // 2.5ms (common servo max)

#define SERVO1_CHANNEL 0 // Base Motor (Servo 1)
#define SERVO2_CHANNEL 1 // Linear Actuator (Servo 2)
#define SERVO3_CHANNEL 2 // Link 3 (Servo 3)
#define SERVO4_CHANNEL 3 // Link 4 (Servo 4)
#define GRIPPER_CHANNEL 4 // Gripper

void setup() {
Serial.begin(9600);
pwm.begin();
pwm.setPWMFreq(SERVO_FREQ);
// Initial positions
pwm.setPWM(SERVO1_CHANNEL, 0, MIN_PULSE);
pwm.setPWM(SERVO2_CHANNEL, 0, MIN_PULSE);
pwm.setPWM(SERVO3_CHANNEL, 0, MIN_PULSE);
pwm.setPWM(SERVO4_CHANNEL, 0, MIN_PULSE);
pwm.setPWM(GRIPPER_CHANNEL, 0, MIN_PULSE);
Serial.println("Arduino initialized");
}

void loop() {
if (Serial.available() > 0) {
String command = Serial.readStringUntil('\n');
command.trim();
Serial.print("Received: '"); Serial.print(command); Serial.println("'");

if (command.startsWith("S")) {
int servo = command.substring(1, 2).toInt();
String value = command.substring(2);
Serial.print("Servo: "); Serial.print(servo); Serial.print(", Value: "); Serial.println(value);

if (servo == 2) {
if (value == "up") {
int pulse = map(45, 0, 180, MIN_PULSE, MAX_PULSE); // Larger step for visibility
pwm.setPWM(SERVO2_CHANNEL, 0, 500);
Serial.print("Servo 2 Up, Pulse: "); Serial.println(500);
} else if (value == "down") {
pwm.setPWM(SERVO2_CHANNEL, 0, 200);
Serial.println("Servo 2 Down, Pulse: MIN_PULSE");
} else if (value == "stop") {
int pulse = map(90, 0, 180, MIN_PULSE, MAX_PULSE);
pwm.setPWM(SERVO2_CHANNEL, 0, 0);
Serial.print("Servo 2 Stop, Pulse: "); Serial.println(pulse);
}
} else {
int angle = value.toInt();
if (angle < 0) angle = 0; // Clamp to valid range
int max_angle = (servo == 1) ? 270 : (servo == 3) ? 360 : 180;
if (angle > max_angle) angle = max_angle;
int pulse = map(angle, 0, max_angle, MIN_PULSE, MAX_PULSE);
Serial.print("Servo "); Serial.print(servo); Serial.print(", Angle: "); Serial.print(angle);
Serial.print(", Pulse: "); Serial.println(pulse);

switch (servo) {
case 1:
pwm.setPWM(SERVO1_CHANNEL, 0, pulse);
break;
case 3:
pwm.setPWM(SERVO3_CHANNEL, 0, pulse);
break;
case 4:
pwm.setPWM(SERVO4_CHANNEL, 0, pulse);
break;
}
}
} else if (command.startsWith("G")) {
int state = command.substring(1).toInt();
Serial.print("Gripper State: "); Serial.println(state);
if (state == 1) {
pwm.setPWM(GRIPPER_CHANNEL, 0, 380);
Serial.println("Gripper Hold, Pulse: MAX_PULSE");
} else {
pwm.setPWM(GRIPPER_CHANNEL, 0, 180);
Serial.println("Gripper Release, Pulse: MIN_PULSE");
}
}
}
}
