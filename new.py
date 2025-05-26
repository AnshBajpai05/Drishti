import threading
import queue
import time
import cv2
import sys
import os

sys.path.append('Module-1')
from new_voice import *

sys.path.append('Module-2')
from new_OCR import *

sys.path.append('Module-3')
from new_cap import *

sys.path.append('Module-4')
from new_sim import *

mode = 0

caption_thread_active = False
recognize_thread_active = False
ocr_thread_active = False
caption_result_queue = queue.Queue()
recognize_result_queue = queue.Queue()
ocr_result_queue = queue.Queue()

def run_caption(frame, result_queue):
    global caption_thread_active
    caption_thread_active = True
    caption_text = caption(frame)
    result_queue.put(caption_text)
    caption_thread_active = False

def run_recognize(frame, result_queue):
    global recognize_thread_active
    recognize_thread_active = True
    result = recognise(frame)
    result_queue.put(result)
    recognize_thread_active = False

def run_ocr(frame, result_queue):
    global ocr_thread_active
    ocr_thread_active = True
    results = ocr(frame)
    result_queue.put(results)
    ocr_thread_active = False

def cam():
    global mode, caption_thread_active, recognize_thread_active, ocr_thread_active
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if not caption_result_queue.empty():
            caption_text = caption_result_queue.get()
            print(f"[Caption]: {caption_text}")
            voice(caption_text)

        if not recognize_result_queue.empty():
            result = recognize_result_queue.get()
            if result == "Unknown":
                print("Could not recognize you. Please come closer.")
                time.sleep(1)
            elif result == "NoFace":
                print("No face detected.")
                time.sleep(1)
            else:
                print(f"Hello {result}")
                mode = 0

        if not ocr_result_queue.empty():
            ocr_output = ocr_result_queue.get()
            if ocr_output:
                for _, text, confidence in ocr_output:
                    if confidence > 0.5 and len(text.strip().split()) > 2:
                        print(f"[OCR]: {text}")
                        voice(text)


        if mode == 0:
            print('.', end='', flush=True)

        elif mode == 1:
            print(1)
            if not caption_thread_active:
                threading.Thread(
                    target=run_caption,
                    args=(frame.copy(), caption_result_queue),
                    daemon=True
                ).start()
                mode = 0

        elif mode == 2:
            print(2)
            if not recognize_thread_active:
                threading.Thread(
                    target=run_recognize,
                    args=(frame.copy(), recognize_result_queue),
                    daemon=True
                ).start()

        elif mode == 3:
            print(3)
            if not ocr_thread_active:
                threading.Thread(
                    target=run_ocr,
                    args=(frame.copy(), ocr_result_queue),
                    daemon=True
                ).start()
                mode = 0

        cv2.imshow("frame", frame)

        key = cv2.waitKey(1)
        if key == 49:  # '1'
            mode = 1
        elif key == 50:  # '2'
            mode = 2
        elif key == 51:  # '3'
            mode = 3
        elif key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    cam()
