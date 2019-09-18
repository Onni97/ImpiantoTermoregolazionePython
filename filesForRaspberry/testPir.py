### NOT WORKING
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
PIR_PIN = 7

GPIO.setup(PIR_PIN, GPIO.IN)

try:
    print("PIR TEST, WAIT")
    time.sleep(2)
    print("OK")

    while True:
        if GPIO.input(PIR_PIN):
            print("✔ MOTION DETECTED")
        else:
            print("❌ MOTION NOT DETECTED")
        time.sleep(1)

except KeyboardInterrupt:
    print("QUIT")
    GPIO.cleanup()