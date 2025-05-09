import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import ttk
import serial
import time
import pyttsx3
import threading
import socket
from PIL import Image, ImageTk
from queue import Queue

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)

speech_queue = Queue()
gui_queue = Queue()
servo_queue = Queue()

arduino = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
time.sleep(2)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

current_control = 1
hand_detected = False
gripper_state = "Release"
current_theme = "dark"
left_hand_state = "Release"
right_hand_state = "Release"
hand_gesture_enabled = True
client_socket = None
last_slider_update = {1: 0, 3: 0, 4: 0}
is_recording = False
recorded_movements = []  # List of (timestamp, command)
recording_start_time = 0
is_playing = False


def speak(text):
    speech_queue.put(text)


def audio_thread():
    while True:
        text = speech_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()
        speech_queue.task_done()


threading.Thread(target=audio_thread, daemon=True).start()


def send_to_arduino(command):
    arduino.write(f"{command}\n".encode())
    time.sleep(0.05)
    if is_recording:
        timestamp = time.time() - recording_start_time
        recorded_movements.append((timestamp, command))
        print(f"Recorded: {timestamp}, {command}")


def servo_update_thread():
    global is_recording, recorded_movements, recording_start_time
    while True:
        servo, position = servo_queue.get()
        if servo is None:
            break
        position = max(0, min(180, position))
        current_time = time.time()
        if current_time - last_slider_update[servo] < 0.2:
            servo_queue.task_done()
            continue
        last_slider_update[servo] = current_time
        if servo == 1:
            position_scaled = int((position / 180) * 270)
            command = f"S1{position_scaled}"
        elif servo == 3:
            position_scaled = int((position / 180) * 360)
            command = f"S3{position_scaled}"
        elif servo == 4:
            position_scaled = position
            command = f"S4{position_scaled}"
        send_to_arduino(command)
        if client_socket:
            try:
                client_socket.send(f"S{servo}{position}\n".encode())
                print(f"Sent to client: S{servo}{position}")
            except Exception as e:
                print(f"Failed to send to client: {e}")
        servo_queue.task_done()


threading.Thread(target=servo_update_thread, daemon=True).start()


def playback_thread(loops, speed):
    global is_playing, recorded_movements
    if not recorded_movements:
        speak("No recorded movements to play")
        print("No recorded movements available")
        return
    is_playing = True
    speak(f"Playing recorded movements for {loops} loops")
    print(f"Starting playback: {len(recorded_movements)} steps, {loops} loops, speed {speed}")
    speed_factor = 2 - (speed / 5)
    total_duration = recorded_movements[-1][0]
    for i in range(int(loops)):
        if not is_playing:
            break
        print(f"Loop {i + 1}/{loops}")
        start_time = time.time()
        for timestamp, command in recorded_movements:
            if not is_playing:
                break
            elapsed = time.time() - start_time
            delay = (timestamp * speed_factor) - elapsed
            if delay > 0:
                time.sleep(delay)
            if command.startswith("S1") or command.startswith("S3") or command.startswith("S4"):
                servo = int(command[1])
                position = int(command[2:])
                servo_queue.put((servo, position))
                gui_queue.put(("set_slider", servo, position))
            elif command.startswith("S2") or command.startswith("G"):
                send_to_arduino(command)
            print(f"Playing: {command} at {timestamp * speed_factor}s")
        while time.time() - start_time < total_duration * speed_factor:
            if not is_playing:
                break
            time.sleep(0.01)
    is_playing = False
    speak("Playback stopped")
    print("Playback completed")


def tcp_server():
    global current_control, client_socket, is_recording, recording_start_time, is_playing
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 12345))
    server_socket.listen(1)
    print("TCP Server listening on port 12345...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to client: {addr}")
        try:
            while True:
                data = client_socket.recv(1024).decode().strip().lower()
                if not data:
                    break
                print(f"Received: '{data}'")

                control_map = {
                    "servo 1": 1,
                    "servo 2": 2,
                    "servo 3": 3,
                    "servo 4": 4,
                    "gripper": 5
                }
                control_names = {1: "Servo 1", 2: "Servo 2", 3: "Servo 3", 4: "Servo 4", 5: "Gripper"}

                try:
                    if data in control_map:
                        current_control = control_map[data]
                        gui_queue.put(("update_control", current_control, control_names[current_control]))
                        speak(f"Control switched to {control_names[current_control]}")
                        client_socket.send(f"Switched to {control_names[current_control]}\n".encode())
                    elif data == "up":
                        current_control = 2
                        gui_queue.put(("update_control", current_control, control_names[current_control]))
                        gui_queue.put(("move_linear", "up"))
                        speak("Servo 2 moving up")
                        client_socket.send("Servo 2 moving up\n".encode())
                    elif data == "down":
                        current_control = 2
                        gui_queue.put(("update_control", current_control, control_names[current_control]))
                        gui_queue.put(("move_linear", "down"))
                        speak("Servo 2 moving down")
                        client_socket.send("Servo 2 moving down\n".encode())
                    elif data == "stop":
                        current_control = 2
                        gui_queue.put(("update_control", current_control, control_names[current_control]))
                        gui_queue.put(("stop_linear", None))
                        speak("Servo 2 stopped")
                        client_socket.send("Servo 2 stopped\n".encode())
                    elif data.startswith("s1"):
                        position = int(data[2:])
                        gui_queue.put(("set_slider", 1, position))
                        servo_queue.put((1, position))
                    elif data.startswith("s3"):
                        position = int(data[2:])
                        gui_queue.put(("set_slider", 3, position))
                        servo_queue.put((3, position))
                    elif data.startswith("s4"):
                        position = int(data[2:])
                        gui_queue.put(("set_slider", 4, position))
                        servo_queue.put((4, position))
                    elif data == "grip":
                        current_control = 5
                        gui_queue.put(("update_control", current_control, control_names[current_control]))
                        gui_queue.put(("gripper_action", "Hold"))
                        speak("Gripper holding")
                        client_socket.send("Gripper holding\n".encode())
                    elif data == "release":
                        current_control = 5
                        gui_queue.put(("update_control", current_control, control_names[current_control]))
                        gui_queue.put(("gripper_action", "Release"))
                        speak("Gripper releasing")
                        client_socket.send("Gripper releasing\n".encode())
                    elif data == "record":
                        is_recording = True
                        recorded_movements.clear()
                        recording_start_time = time.time()
                        speak("Recording started")
                        client_socket.send("Recording started\n".encode())
                    elif data == "stop_recording":
                        is_recording = False
                        speak("Recording stopped")
                        client_socket.send("Recording stopped\n".encode())
                    elif data.startswith("play"):
                        parts = data.split()
                        loops = int(parts[1]) if len(parts) > 1 else 1
                        speed = int(parts[2]) if len(parts) > 2 else 5
                        threading.Thread(target=playback_thread, args=(loops, speed), daemon=True).start()
                        client_socket.send(f"Playing for {loops} loops at speed {speed}\n".encode())
                    elif data == "stop_playback":
                        is_playing = False
                        speak("Playback stopped")
                        client_socket.send("Playback stopped\n".encode())
                    else:
                        client_socket.send("Invalid command\n".encode())
                except Exception as e:
                    print(f"Error: {e}")
                    client_socket.send(f"Error: {str(e)}\n".encode())
        except Exception as e:
            print(f"TCP Client error: {e}")
        finally:
            client_socket.close()
            client_socket = None
            print(f"Disconnected from client: {addr}")


threading.Thread(target=tcp_server, daemon=True).start()


def show_loading_screen(root):
    loading_window = tk.Toplevel(root)
    loading_window.overrideredirect(True)
    loading_window.geometry(
        "600x400+{}+{}".format(int(root.winfo_screenwidth() / 2 - 300), int(root.winfo_screenheight() / 2 - 200)))
    loading_window.configure(bg="#15202B")

    loading_label = tk.Label(loading_window, text="Your SCARA Control Panel is Loading", font=("Helvetica", 20, "bold"),
                             bg="#15202B", fg="#FFFFFF", wraplength=500)
    loading_label.place(relx=0.5, rely=0.4, anchor="center")

    bar_width = 400
    bar_height = 20
    loading_canvas = tk.Canvas(loading_window, width=bar_width, height=bar_height, bg="#15202B", highlightthickness=0)
    loading_canvas.place(relx=0.5, rely=0.6, anchor="center")
    loading_canvas.create_rectangle(0, 0, bar_width, bar_height, fill="#333333", outline="#FFFFFF")
    progress_bar = loading_canvas.create_rectangle(0, 0, 0, bar_height, fill="#1DA1F2", outline="")

    keep_animating = True

    def fade_text(step=0):
        nonlocal keep_animating
        if not loading_window.winfo_exists() or not keep_animating:
            return
        shades = ["#333333", "#666666", "#999999", "#CCCCCC", "#FFFFFF", "#CCCCCC", "#999999", "#666666"]
        color = shades[step % len(shades)]
        loading_label.configure(fg=color)
        loading_window.after(200, fade_text, step + 1)

    def update_loading_bar(progress=0):
        nonlocal keep_animating
        if not loading_window.winfo_exists() or not keep_animating:
            return
        new_width = (progress / 100) * bar_width
        loading_canvas.coords(progress_bar, 0, 0, new_width, bar_height)
        if progress < 100:
            loading_window.after(30, update_loading_bar, progress + 1)

    fade_text()
    update_loading_bar()
    speak("Your SCARA Control Panel is Loading")

    def close_loading():
        nonlocal keep_animating
        keep_animating = False
        loading_window.destroy()
        setup_main_gui(root)
        root.deiconify()

    loading_window.after(3000, close_loading)


def setup_main_gui(root):
    def toggle_theme():
        global current_theme
        current_theme = "light" if current_theme == "dark" else "dark"
        style.theme_use("clam")
        if current_theme == "dark":
            root.configure(bg="#15202B")
            style.configure("TFrame", background="#15202B")
            style.configure("TLabel", background="#15202B", foreground="#FFFFFF", font=("Helvetica", 12))
            style.configure("TButton", background="#1DA1F2", foreground="#FFFFFF", borderwidth=0,
                            font=("Helvetica", 10, "bold"))
            style.map("TButton", background=[("active", "#1991DA")])
            control_frame.configure(bg="#15202B")
            playback_frame.configure(bg="#15202B")
        else:
            root.configure(bg="#FFFFFF")
            style.configure("TFrame", background="#FFFFFF")
            style.configure("TLabel", background="#FFFFFF", foreground="#000000", font=("Helvetica", 12))
            style.configure("TButton", background="#1DA1F2", foreground="#FFFFFF", borderwidth=0,
                            font=("Helvetica", 10, "bold"))
            style.map("TButton", background=[("active", "#1991DA")])
            control_frame.configure(bg="#FFFFFF")
            playback_frame.configure(bg="#FFFFFF")
        update_widget_colors()

    def update_widget_colors():
        bg_color = "#15202B" if current_theme == "dark" else "#FFFFFF"
        fg_color = "#FFFFFF" if current_theme == "dark" else "#000000"
        for widget in control_frame.winfo_children() + playback_frame.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, ttk.Label):
                widget.configure(bg=bg_color, fg=fg_color)
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=bg_color)

    def toggle_control_mode():
        global hand_gesture_enabled
        hand_gesture_enabled = not hand_gesture_enabled
        mode_text = "Hand Gesture Control" if hand_gesture_enabled else "Manual Control"
        control_mode_label.config(text=f"Mode: {mode_text}")
        speak(f"Switched to {mode_text}")

    def set_slider(servo, position):
        global servo1_slider, servo3_slider, servo4_slider
        position = max(0, min(180, position))
        print(f"Setting slider {servo} to {position}")
        if servo == 1 and servo1_slider:
            servo1_slider.set(position)
        elif servo == 3 and servo3_slider:
            servo3_slider.set(position)
        elif servo == 4 and servo4_slider:
            servo4_slider.set(position)

    def gripper_action(state):
        global gripper_state
        print(f"Gripper action called: state={state}, current_control={current_control}, is_recording={is_recording}")
        if current_control == 5:
            if state == "Hold":
                gripper_state = "Hold"
                send_to_arduino("G1")
                gripper_label.config(text="Gripper: Hold")
                print("Gripper set to Hold")
            elif state == "Release":
                gripper_state = "Release"
                send_to_arduino("G0")
                gripper_label.config(text="Gripper: Release")
                print("Gripper set to Release")

    def start_recording():
        global is_recording, recorded_movements, recording_start_time
        is_recording = True
        recorded_movements.clear()
        recording_start_time = time.time()
        speak("Recording started")
        print("Recording started")
        if client_socket:
            client_socket.send("Recording started\n".encode())

    def stop_recording():
        global is_recording
        is_recording = False
        speak("Recording stopped")
        print("Recording stopped")
        if client_socket:
            client_socket.send("Recording stopped\n".encode())

    def play_recording():
        loops = loop_entry.get()
        speed = playback_speed.get()
        try:
            loops = int(loops)
            threading.Thread(target=playback_thread, args=(loops, speed), daemon=True).start()
            speak(f"Playing for {loops} loops at speed {speed}")
            if client_socket:
                client_socket.send(f"Playing for {loops} loops at speed {speed}\n".encode())
        except ValueError:
            speak("Invalid number of loops")

    def stop_playback():
        global is_playing
        is_playing = False
        speak("Playback stopped")
        if client_socket:
            client_socket.send("Playback stopped\n".encode())

    def process_gui_queue():
        try:
            while not gui_queue.empty():
                action, *args = gui_queue.get_nowait()
                print(f"GUI queue: {action}, {args}")
                if action == "update_control":
                    servo_num, name = args
                    control_button.config(text=f"Switch Control ({name})")
                elif action == "move_linear":
                    direction = args[0]
                    move_linear_actuator(direction)
                elif action == "stop_linear":
                    stop_linear_actuator()
                elif action == "set_slider":
                    servo, position = args
                    set_slider(servo, position)
                elif action == "gripper_action":
                    state = args[0]
                    gripper_action(state)
                gui_queue.task_done()
        except Exception as e:
            print(f"GUI queue error: {e}")
        root.after(100, process_gui_queue)

    root.configure(bg="#15202B")
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background="#15202B")
    style.configure("TLabel", background="#15202B", foreground="#FFFFFF", font=("Helvetica", 12))
    style.configure("TButton", background="#1DA1F2", foreground="#FFFFFF", borderwidth=0,
                    font=("Helvetica", 10, "bold"))
    style.map("TButton", background=[("active", "#1991DA")])

    camera_frame = tk.Label(root, bg="#15202B")
    camera_frame.place(x=10, y=10, width=640, height=480)

    global control_frame, servo1_slider, servo3_slider, servo4_slider, left_hand_state_label, right_hand_state_label, control_button, gripper_label, playback_frame, loop_entry, playback_speed
    control_frame = tk.Frame(root, bg="#15202B")
    control_frame.place(x=660, y=10, width=320, height=580)

    playback_frame = tk.Frame(root, bg="#15202B")
    playback_frame.place(x=10, y=490, width=640, height=200)

    record_label = tk.Label(playback_frame, text="Motion Recording & Playback", bg="#15202B", fg="#FFFFFF",
                            font=("Helvetica", 12, "bold"))
    record_label.pack(pady=5)

    record_frame = tk.Frame(playback_frame, bg="#15202B")
    record_frame.pack(pady=5)
    record_button = ttk.Button(record_frame, text="Record", command=start_recording, style="TButton")
    record_button.pack(side=tk.LEFT, padx=5)
    stop_record_button = ttk.Button(record_frame, text="Stop Recording", command=stop_recording, style="TButton")
    stop_record_button.pack(side=tk.LEFT, padx=5)

    play_frame = tk.Frame(playback_frame, bg="#15202B")
    play_frame.pack(pady=5)
    play_button = ttk.Button(play_frame, text="Play", command=play_recording, style="TButton")
    play_button.pack(side=tk.LEFT, padx=5)
    stop_play_button = ttk.Button(play_frame, text="Stop", command=stop_playback, style="TButton")
    stop_play_button.pack(side=tk.LEFT, padx=5)

    loop_frame = tk.Frame(playback_frame, bg="#15202B")
    loop_frame.pack(pady=5)
    loop_label = tk.Label(loop_frame, text="Loops:", bg="#15202B", fg="#FFFFFF")
    loop_label.pack(side=tk.LEFT, padx=5)
    loop_entry = tk.Entry(loop_frame, width=5, bg="#333333", fg="#FFFFFF", insertbackground="#FFFFFF")
    loop_entry.insert(0, "1")
    loop_entry.pack(side=tk.LEFT)

    speed_frame = tk.Frame(playback_frame, bg=
