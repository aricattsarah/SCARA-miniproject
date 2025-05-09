🤖 SCARA Robot Controller

This project provides a complete control system for a SCARA (Selective Compliance Articulated Robot Arm) using Arduino and Python, enhanced with three different control modes:

1. Hand Gesture Control


2. GUI Control Panel


3. Mobile App Control via Flutter



The SCARA arm is operated using servo motors through an Adafruit 16-channel PWM driver and communicates via serial (USB) and Wi-Fi.


---

🗂️ Project Structure

SCARA-ROBOT/
├── Arduino/
│   └── scara_controller.ino        # Main Arduino code
├── Python/
│   └── hand_gesture.py             # Serial communication & gesture control
├── Flutter/
│   └── flutter_controller.dart     # Mobile app for wireless control
├── README.md


---

⚙️ Hardware Requirements

Arduino Uno or Mega

Adafruit 16-Channel PWM Servo Driver (PCA9685)

Servo Motors (at least 4 + 1 for gripper)

External Power Supply (for servo motors)

USB Cable (for Arduino-PC communication)



---

💻 Software Requirements

Arduino Side

Arduino IDE

Adafruit PWM Servo Driver Library


Python Side

Python 3.10+

pyserial (pip install pyserial)

Optional: PyCharm for editing and running Python scripts


Flutter Side

Flutter SDK

Dart

Android Studio (or VS Code)

Android phone on same Wi-Fi network as host PC



---

🚀 How to Use

1. Upload Arduino Code

Open Arduino/scara_controller.ino in the Arduino IDE.

Select the correct board and COM port.

Upload the code to your Arduino board.


2. Run Python Gesture Control

Edit the COM port in Python/hand_gesture.py:


arduino = serial.Serial(port='COM3', baudrate=9600, timeout=1)

Run the script to start serial communication and control via hand gestures.


3. Use Flutter App for Mobile Control

Ensure both your PC and Android phone are connected to the same Wi-Fi.

Run the Flutter app in Flutter/flutter_controller.dart on your mobile device.

The app sends control signals to the PC or directly to the robot (depending on setup).



---

📌 Notes

Use a separate power supply for servo motors to avoid brownouts or resets.

Check servo limits in the code to prevent hardware damage.

For gesture control, you may need additional hardware like a flex sensor or MPU6050
