# 🤖 SCARA Robot Controller
This project provides the Arduino and Python code to control a SCARA (Selective Compliance Articulated Robot Arm) using an Adafruit 16-channel PWM driver, servo motors, and serial communication.
3 types of countrol are implemented
1. Hand gesture control
2. Control via a control panel
3. Control via Flutter (Android phone)

## 🛠️ Project Structure
## ⚙️ Hardware Requirements

- Arduino Uno / Mega
- Adafruit 16-Channel PWM Servo Driver (PCA9685)
- Servo motors (4+1 gripper)
- External power supply for servos
- USB cable for serial communication
## Software Requirements

### Arduino Side
- [Adafruit PWM Servo Driver Library](https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library)
- Arduino IDE

### Python Side
- Python 3.10+
- `pyserial` package (`pip install pyserial`)
- PyCharm

## How to Use

### 1. Upload Arduino Code
Upload the code from `SCARA-ROBOT/scara_controller.ino` to your Arduino board using the Arduino IDE.

### 2. Run Python Serial Interface

Update `SCARA-ROBOT/hand_gesture.py` with your correct COM port:

`python

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)

### 3. Run the flutter code alone to control the arm via a mobile app (flutter.dart)
- ensure same wifi is connected by the device and the android mobile  
