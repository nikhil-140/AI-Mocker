import datetime
import webview
import keyboard
import tkinter as tk
from tkinter import messagebox
import cv2
import threading
import winsound
import matplotlib.pyplot as plt

def show_warning(message):
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("Warning", message)
    root.destroy()

def play_sound_and_show_warning():
    frequency = 300
    duration = 1000
    winsound.Beep(frequency, duration)
    show_warning("No face detected! Please make sure your face is visible to the camera Otherwise, the form will be submitted automatically.")

def open_camera(stop_event):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    no_face_detected_count = 0
    window_name = "Camera"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 100, 100)

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(10, 10))

        if len(faces) > 0:
            no_face_detected_count = 0
        else:
            no_face_detected_count += 1
            if no_face_detected_count >= 30:
                play_sound_and_show_warning()
                no_face_detected_count = 0 

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def open_webview(url):
    stop_event = threading.Event()
    window = webview.create_window('Webpage', url, fullscreen=True)
    camera_thread = threading.Thread(target=open_camera, args=(stop_event,), daemon=True)
    camera_thread.start()

    def on_esc(e):
        print("ESC key pressed. Closing the webview and stopping the camera...")
        window.destroy()
        stop_event.set()
        camera_thread.join()
        keyboard.unhook_all()

    keyboard.on_press_key('esc', on_esc)
    webview.start()
    keyboard.wait('esc')
url = "http://localhost/TECHEX/log.php"
open_webview(url)