import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
while True: # Run forever
    if GPIO.input(10) == GPIO.HIGH:
        print("Button 10 was pushed!")
    if GPIO.input(8) == GPIO.HIGH:
        print("Button 8 was pushed!")
    if GPIO.input(12) == GPIO.HIGH:
        print("Button 12 was pushed!")
    if GPIO.input(11) == GPIO.HIGH:
        print("Button 11 was pushed!")
    if GPIO.input(13) == GPIO.HIGH:
        print("Button 13 was pushed!")
    if GPIO.input(15) == GPIO.HIGH:
        print("Button 15 was pushed!")
