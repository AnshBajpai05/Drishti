# Install the assemblyai package by executing the command "pip install assemblyai"
import threading
import logging
from typing import Type
from picamera2 import Picamera2, Preview
from time import sleep
import cv2
import sys
import os
from dotenv import load_dotenv, dotenv_values 
from ultralytics import YOLO
import string
import assemblyai as aai
from assemblyai.streaming.v3 import (
    BeginEvent,
    StreamingClient,
    StreamingClientOptions,
    StreamingError,
    StreamingEvents,
    StreamingParameters,
    StreamingSessionParameters,
    TerminationEvent,
    TurnEvent,
)
from ultrasonic import run_distance

sys.path.append('Module-1')
from new_voice import *

sys.path.append('Module-2')
from new_OCR import *

sys.path.append('Module-3')
from new_cap import *

sys.path.append('Module-4')
from new_sim import *

load_dotenv()

api_key = os.getenv("AAI_API_KEY")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

picam2 = Picamera2()

last_trigger_time = 0  # Global debounce tracker
TRIGGER_COOLDOWN = 5   # seconds
last_trigger_phrase = ""

model = YOLO('yolov8n.pt')

def on_begin(self: Type[StreamingClient], event: BeginEvent):
    print(f"Session started: {event.id}")
        
def on_turn(self: Type[StreamingClient], event: TurnEvent):
    global last_trigger_time
    global last_trigger_phrase
    transcript = event.transcript.lower()
    print(f"{transcript} ({event.end_of_turn})")

    trigger_phrase = "what is in front of me"

    current_time = time.time()

    if (
        trigger_phrase in transcript
        and event.end_of_turn
        and transcript != last_trigger_phrase
        and (current_time - last_trigger_time > TRIGGER_COOLDOWN)
    ):
        last_trigger_time = current_time
        last_trigger_phrase = transcript  # Save to prevent repeat

        print("--------------Trigger phrase detected. Capturing image...----------------")

        picam2.start()
        frame = picam2.capture_array()
        picam2.stop()
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        
        cap = caption(frame)
        print("--------Caption:", cap)
        voice(cap)
        
    if (
        "capture image of" in transcript
        and event.end_of_turn
        and transcript != last_trigger_phrase
        and (current_time - last_trigger_time > TRIGGER_COOLDOWN)
    ):
        print("--------------Trigger phrase detected. Capturing image...----------------")
        
        name = ""
        raw_name = ""
        
        try:
            raw_name = transcript.split("capture image of")[-1].strip().capitalize()
            name = raw_name.translate(str.maketrans('', '', string.punctuation)).capitalize()
        except IndexError:
            print("Could not extract name from transcript.")
            return
            
        if len(name) != 0:
            folder_path = f"./Module-4/faces/{name}"
            os.makedirs(folder_path, exist_ok=True)

            existing = os.listdir(folder_path)
            count = len([f for f in existing if f.endswith(".jpg")])

            picam2.start()
            frame = picam2.capture_array()
            picam2.stop()
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        
            cv2.imwrite(f"{folder_path}/{count}.jpg", frame)
            print(f"Image saved at: {folder_path}")
            train_faces()
        
    if (
        "read this" in transcript
        and event.end_of_turn
        and transcript != last_trigger_phrase
        and (current_time - last_trigger_time > TRIGGER_COOLDOWN)
    ):
        last_trigger_time = current_time
        last_trigger_phrase = transcript
        print("--------------Trigger phrase detected. Capturing image...----------------")
        picam2.start()
        frame = picam2.capture_array()
        picam2.stop()
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        ocr_out = ocr(frame)
        #ocr_out = mmocr(frame)
        print("----OCR------------\n")
        #print(ocr_out)
        
        if ocr_out:
            for _,text,conf in ocr_out:
                print("\n\n",text,"   ",conf)
                if conf>0.2:
                    print(text)
                    voice(text)
        
    if (
        "detect object" in transcript
        and event.end_of_turn
        and transcript != last_trigger_phrase
        and (current_time - last_trigger_time > TRIGGER_COOLDOWN)
    ):
        print("--------------Trigger phrase detected. Capturing image...----------------")
        last_trigger_time = current_time
        last_trigger_phrase = transcript  # Save to prevent repeat
        picam2.start()
        frame = picam2.capture_array()
        picam2.stop()
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        #print(frame.shape)
        yolo_out = model(frame[:,:,:3])
        class_ids = yolo_out[0].boxes.cls.cpu().numpy().astype(int)
        object_names = [model.names[c] for c in class_ids]
        print("_____________yolo__",object_names)
        if object_names!=[]:
            voice("I see a "+object_names[0])
        else:
            voice("I could not detect anything")
        #print("-----Yolo ------:",yolo_out)
		
    if (
        "who is this" in transcript
        and event.end_of_turn
        and transcript != last_trigger_phrase
        and (current_time - last_trigger_time > TRIGGER_COOLDOWN)
    ):
        print("--------------Trigger phrase detected. Capturing image...----------------")
        last_trigger_time = current_time
        last_trigger_phrase = transcript  # Save to prevent repeat
        picam2.start()
        frame = picam2.capture_array()
        picam2.stop()
        frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        rec_out = recognise(frame)
        print("------Recognized: ", rec_out)
        voice(rec_out)
        

    if event.end_of_turn and not event.turn_is_formatted:
        params = StreamingSessionParameters(format_turns=True)
        self.set_params(params)
        


def on_terminated(self: Type[StreamingClient], event: TerminationEvent):
    print(
        f"Session terminated: {event.audio_duration_seconds} seconds of audio processed"
    )


def on_error(self: Type[StreamingClient], error: StreamingError):
    print(f"Error occurred: {error}")


def main():
    client = StreamingClient(
        StreamingClientOptions(
            api_key=api_key,
            api_host="streaming.assemblyai.com",
        )
    )
    voice("  Hello, I am Drishti, How may I help you")
    client.on(StreamingEvents.Begin, on_begin)
    client.on(StreamingEvents.Turn, on_turn)
    client.on(StreamingEvents.Termination, on_terminated)
    client.on(StreamingEvents.Error, on_error)

    client.connect(
        StreamingParameters(
            sample_rate=16000,
            format_turns=True,
        )
    )

    try:
        client.stream(
          aai.extras.MicrophoneStream(sample_rate=16000)
        )
    finally:
        client.disconnect(terminate=True)


if __name__ == "__main__":
    my_thread = threading.Thread(target=run_distance)
    my_thread.start()
    main()
