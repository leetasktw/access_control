import time
import RPi.GPIO as GPIO

def doReMi():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(12, GPIO.OUT)
    p = GPIO.PWM(12, 50)
    p.start(50)   
    try:
        while True:
            print("Do")
            p.ChangeFrequency(1047)
            time.sleep(0.5)
    except KeyboardInterrupt:       
        p.stop()
        GPIO.cleanup()

doReMi()