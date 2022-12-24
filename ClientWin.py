from multiprocessing import Process
from lcd import *
import socket
import threading
import cv2
import RPi.GPIO as GPIO  # Import Raspberry Pi GPIO library
GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering

cam = cv2.VideoCapture(0)

GPIO.setwarnings(False)  # Ignore warning for now
GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(15, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

sentence = ''
isPressedSpace = False
isPressedBackspace = False
isPressedReset = False
isPressedNext = False
isPressedBack = False
img_name = "img.jpg"
message1 = ''
message2 = ''
index = len(sentence)


def setup_connection():
    # AF_INET = IP, SOCK_STREAM = TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('192.168.16.106', 1002))
    return client


def send_image(path):
    client = setup_connection()
    file = open(path, "rb")
    imgae_data = file.read(2048)  # stream-based protocol

    while imgae_data:
        client.send(imgae_data)
        imgae_data = file.read(2048)
    print('sent img to server')
    file.close()
    client.close()


def splitLineLCD(res):
    s1 = res[0: 16]
    s2 = res[16: len(res)]
    if len(s2) >= 16:
        tmp1 = res[len(res)-32:]
        s1 = tmp1[0:16]
        s2 = tmp1[16:]
    else:
        if len(s1) < 16:
            s1 = res
        elif len(s2) < 16:
            s2 = res[16: len(res)]
    return s1, s2


def findSentenceByIndex(sentence, index):
    return sentence[0:index]

# stream-based protocol


def receive_message():
    global index
    global sentence
    # AF_INET = IP, SOCK_STREAM = TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('192.168.16.106', 1002))
    msg = ''
    while not msg:
        msg = client.recv(2048).decode()
    if msg != 'unknown':
        sentence += msg
    else:
        print(msg)
    print(sentence)
    index = len(sentence)
    client.close()


def lcd(mes1, mes2):
    print(mes1)
    print(mes2)


if __name__ == "__main__":

    while True:
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cv2.imshow("handSignal", frame)
        k = cv2.waitKey(1)
        if k % 256 == 27:
            print("Escape hit, closing...")
            break
        elif k % 256 == 51:
            print("close connect to server")
            break

        # button pressed capture img
        elif GPIO.input(10) == GPIO.HIGH:
            cv2.imwrite(img_name, frame)
            send_image(img_name)
            receive_message()
            message1, message2 = splitLineLCD(sentence)
            lcd(message1, message2)

        # space
        elif GPIO.input(13) == GPIO.HIGH:
            if not isPressedSpace:
                sentence += ' '
                isPressedSpace = True
                message1, message2 = splitLineLCD(sentence)
                lcd(message1, message2)
                index = len(sentence)
        elif GPIO.input(12) == GPIO.LOW:
            isPressedSpace = False

        # backspace
        if GPIO.input(11) == GPIO.HIGH:
            if not isPressedBackspace:
                sentence = sentence[0: len(sentence) - 1]
                message1, message2 = splitLineLCD(sentence)
                lcd(message1, message2)
                index = len(sentence)
                isPressedBackspace = True
        elif GPIO.input(11) == GPIO.LOW:
            isPressedBackspace = False

        # reset
        if GPIO.input(12) == GPIO.HIGH:
            sentence = ''
            message1, message2 = splitLineLCD(sentence)
            lcd(message1, message2)
            index = 0
            isPressedReset = True
        elif GPIO.input(12) == GPIO.LOW:
            isPressedReset = False

        # back
        if GPIO.input(8) == GPIO.HIGH and len(sentence) > 32 and index > 0:
            index -= 1
            res = findSentenceByIndex(sentence, index)
            message1, message2 = splitLineLCD(res)
            lcd(message1, message2)
            isPressedBack = True
        elif GPIO.input(8) == GPIO.LOW:
            isPressedBack = False

        # next
        if GPIO.input(15) == GPIO.HIGH and index < len(sentence):
            index += 1
            res = findSentenceByIndex(sentence, index)
            message1, message2 = splitLineLCD(res)
            lcd(message1, message2)
            isPressedNext = True
        elif GPIO.input(15) == GPIO.LOW:
            isPressedNext = False
