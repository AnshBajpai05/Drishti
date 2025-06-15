from gpiozero import DistanceSensor, OutputDevice
from time import sleep

TRIGGER_PIN = 23
ECHO_PIN = 24
VIBRATOR_PIN = 21

vibrator = OutputDevice(VIBRATOR_PIN)
sensor = DistanceSensor(echo=ECHO_PIN, trigger=TRIGGER_PIN, max_distance=2.0)

def run_distance():
    while True:
        dist = sensor.distance * 100  # convert to cm
        print(f"Distance: {dist:.2f} cm")
        sleep(0.5)
        if dist != False and dist < 25:
            vibrator.on()
            sleep(1)
            vibrator.off()
            sleep(5)
