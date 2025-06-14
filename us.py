import lgpio as GPIO
import time
TRIG = 23
ECHO = 24

h = GPIO.gpiochipp_open(0)
GPIO.gpio_claim_input(h, ECHO)
GPIO.gpio_claim_output(h, TRIG)

def get_distance():
    GPIO.gpio_write(h, TRIG, 0)
    time.sleep(2)
    
    GPIO.gpio_write(h, TRIG, 1)
    time.sleep(0.00001)
    GPIO.gpio_write(h, TRIG, 0)

    while GPIO.gpio_read(h, ECHO) == 0:
        start_time = time.time()

    while GPIO.gpio_read(h, ECHO) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Speed of sound is approximately 34300 cm/s
    return distance

if __name__ == "__main__":
    try:
        while True:
            dist = get_distance()
            print(f"Distance: {dist:.2f} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Measurement stopped by User")
    finally:
        GPIO.gpiochipp_close(h)