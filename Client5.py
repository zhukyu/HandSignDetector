import socket
import threading
import cv2
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
from lcd import *
from multiprocessing import Process

cam = cv2.VideoCapture(0)

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

sentence = ''
isPressed = False
img_name = "img.jpg"

def setup_connection():
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
  client.connect(('192.168.43.165', 1002))
  return client

def capture_img():
  global sentence
  global img_name
  #cv2.namedWindow("test")
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
    #button pressed
    elif GPIO.input(10) == GPIO.HIGH:
      cv2.imwrite(img_name, frame)
      break
    elif k % 256 == 51:
      print("close connect to server")
      break
    elif GPIO.input(8) == GPIO.HIGH:
        if not isPressed:
            sentence += ' '
            isPressed = True
    elif GPIO.input(8) == GPIO.LOW:
        isPressed = False  
    if GPIO.input(12) == GPIO.HIGH:
        sentence = ''

  return img_name

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

# stream-based protocol
def receive_message():
    global sentence
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # AF_INET = IP, SOCK_STREAM = TCP
    client.connect(('192.168.43.165', 1002))
    msg = ''
    while not msg:
      msg = client.recv(2048).decode()
    if msg != 'unknown':
        sentence += msg
    else:
        print(msg)
    print(sentence)
    client.close()
    
def get_id(tmp):

        # returns id of the respective thread
        if hasattr(tmp, '_thread_id'):
            return tmp._thread_id
        for id, thread in threading._active.items():
            if thread is tmp:
                return id
def raise_exception(tmp):
        thread_id = tmp.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')
                
if __name__ == "__main__":
  
  while True:
    t1 = threading.Thread(target=send_image, args=(capture_img(),))
    t2 = threading.Thread(target=receive_message, args=())
    t1.start()
    t1.join()
    t2.start()
    t2.join()
    t3 = Process(target=lcd, args=(sentence,))
    t3.start()
