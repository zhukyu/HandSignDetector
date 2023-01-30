import socket
import threading
import cv2
from cvzone.HandTrackingModule import HandDetector
from keras.applications.vgg16 import VGG16
from keras.layers import Input, Flatten, Dense, Dropout
from keras.models import Model
import numpy as np
import math

# init model
detector = HandDetector(maxHands=1)
weight = "Model/vggmodel.h5"

# AF_INET = IP, SOCK_STREAM = TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('', 1002))  # 127.0.0.1
server.listen(1)

message_content = "unknown"

def get_model():
    model_vgg16_conv = VGG16(weights='imagenet', include_top=False)

    # Dong bang cac layer
    for layer in model_vgg16_conv.layers:
        layer.trainable = False

    # Tao model
    input = Input(shape=(128, 128, 3), name='image_input')
    output_vgg16_conv = model_vgg16_conv(input)

    # Them cac layer FC va Dropout
    x = Flatten(name='flatten')(output_vgg16_conv)
    x = Dense(4096, activation='relu', name='fc1')(x)
    x = Dropout(0.5)(x)
    x = Dense(4096, activation='relu', name='fc2')(x)
    x = Dropout(0.5)(x)
    x = Dense(26, activation='softmax', name='predictions')(x)

    # Compile
    my_model = Model(inputs=input, outputs=x)
    my_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return my_model

def predict(image):
    image = cv2.resize(image, dsize=(128, 128))
    image = image.astype('float')*1./255
    # Convert to tensor
    image = np.expand_dims(image, axis=0)

    predict = model.predict(image)
    print("This picture is: ", labels[np.argmax(predict[0])], (predict[0]))
    print(np.max(predict[0],axis=0))

    return labels[np.argmax(predict[0])]
        
def detect():

    global message_content
    message_content = "unknown"
    offset = 20
    imgSize = 128

    try:
        img = cv2.imread('server_image.jpg')
        hands, img = detector.findHands(img)
        if hands:
            hand = hands[0]
            x, y, w, h = hand['bbox']

            imgWhite = np.ones((imgSize, imgSize, 3), np.uint8)*255
            imgCrop = img[y-offset:y + h+offset, x-offset:x + w+offset]

            aspectRatio = h/w

            if aspectRatio > 1:
                k = imgSize/h
                widthCal = math.ceil(k*w)
                imgResize = cv2.resize(imgCrop, (widthCal, imgSize))
                widthGap = math.ceil((imgSize-widthCal)/2)
                imgWhite[:, widthGap:widthCal+widthGap] = imgResize
                cv2.imwrite("ImageWhite.jpg", imgWhite)
                message_content = predict(imgWhite)


            else:
                k = imgSize/w
                heightCal = math.ceil(k * h)
                imgResize = cv2.resize(imgCrop, (imgSize, heightCal))
                heightGap = math.ceil((imgSize - heightCal) / 2)
                imgWhite[heightGap:heightCal + heightGap, :] = imgResize
                cv2.imwrite("ImageWhite.jpg", imgWhite)
                message_content = predict(imgWhite)
    except:
        print("can't resize image!")

def receive_data():
    client_socket, client_address = server.accept()
    print('connected with {} to receive'.format(client_address))
    global img_count
    file = open('server_image.jpg', "wb")
    image_chunk = client_socket.recv(2048)  # stream-based protocol
    while image_chunk:
        file.write(image_chunk)
        image_chunk = client_socket.recv(2048)
    file.close()
    client_socket.close()
    detect()


def send_message(msg):
    client_socket, client_address = server.accept()
    print('connected with {} to send'.format(client_address))
    client_socket.send(msg.encode())
    client_socket.close()

# init labels
labels = list()
file_object  = open("Model/labels.txt", "r")
while True:
    a = file_object.readline().split()
    if a is None or len(a) == 0 or a is EOFError:
        break
    else:
        labels.append(a[1])
# init model
model = get_model()
model.load_weights(weight)

if __name__ == "__main__":
    while True:
        receive_data()
        print(message_content)
        send_message(message_content)
